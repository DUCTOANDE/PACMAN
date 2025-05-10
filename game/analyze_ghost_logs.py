import json
import os
import matplotlib.pyplot as plt
import numpy as np
import glob
import pygame
import sys
from .constants import*  # Import constants

def load_ghost_log(filepath):
    """Đọc dữ liệu từ file nhật ký ghost."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Lỗi khi tải file nhật ký: {e}")
        return None

def analyze_ghost_logs(data):
    """Phân tích dữ liệu nhật ký di chuyển của ma và trả về các chỉ số."""
    metrics = {}
    for ghost_name, log in data.items():
        movements = log.get('movements', [])
        step_count = len(movements)
        total_distance = 0
        if len(movements) > 1:
            for i in range(1, len(movements)):
                x1, y1 = movements[i-1]['position']
                x2, y2 = movements[i]['position']
                total_distance += ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        start_time = movements[0]['time'] if movements else 0
        end_time = movements[-1]['time'] if movements else 0
        total_time = (end_time - start_time) / 1000.0 if end_time > start_time else 1.0  # Convert ms to seconds
        # Approximate optimal distance (Manhattan distance from start to player position)
        if movements:
            start_pos = movements[0]['position']
            end_pos = movements[-1]['position']
            optimal_distance = abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])
        else:
            optimal_distance = total_distance
        average_speed = total_distance / total_time if total_time > 0 else 0
        path_efficiency = optimal_distance / total_distance if total_distance > 0 else 1
        algorithm = log.get('algorithm', 'Unknown')
        metrics[ghost_name] = {
            'step_count': step_count,
            'average_speed': average_speed,
            'path_efficiency': path_efficiency,
            'algorithm': algorithm
        }
    return metrics

def compare_algorithms(metrics):
    """So sánh hiệu quả của các thuật toán dựa trên các chỉ số."""
    comparison = {}
    for ghost_name, metric in metrics.items():
        algorithm = metric['algorithm']
        if algorithm not in comparison:
            comparison[algorithm] = {
                'ghosts': [],
                'avg_step_count': 0,
                'avg_speed': 0,
                'avg_path_efficiency': 0,
                'instances': 0
            }
        comparison[algorithm]['ghosts'].append(ghost_name)
    for algorithm, data in comparison.items():
        ghosts = data['ghosts']
        if not ghosts:
            continue
        total_step_count = sum(metrics[ghost]['step_count'] for ghost in ghosts)
        total_speed = sum(metrics[ghost]['average_speed'] for ghost in ghosts)
        total_efficiency = sum(metrics[ghost]['path_efficiency'] for ghost in ghosts)
        count = len(ghosts)
        comparison[algorithm]['avg_step_count'] = total_step_count / count
        comparison[algorithm]['avg_speed'] = total_speed / count
        comparison[algorithm]['avg_path_efficiency'] = total_efficiency / count
        comparison[algorithm]['instances'] = count
    return comparison

def evaluate_algorithms(comparison):
    """Đánh giá tổng thể các thuật toán dựa trên các chỉ số."""
    scores = {}
    for algorithm, stats in comparison.items():
        score = (stats['avg_path_efficiency'] * 50 +
                 stats['avg_speed'] * 30 -
                 stats['avg_step_count'] * 0.2)
        scores[algorithm] = score
    return scores

def save_comparison_to_file(comparison):
    """Lưu kết quả so sánh vào file."""
    try:
        with open('algorithm_comparison.json', 'w') as f:
            json.dump(comparison, f, indent=4)
        print("Kết quả so sánh đã được lưu vào algorithm_comparison.json")
    except Exception as e:
        print(f"Lỗi khi lưu so sánh: {e}")

def visualize_evaluation(scores, metrics, from_game=True):
    """Trực quan hóa đánh giá các thuật toán bằng nhiều loại biểu đồ."""
    output_dir = "log"
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(10, 6))
    bars = plt.bar(scores.keys(), scores.values(), color=['skyblue', 'lightgreen', 'salmon', 'lightblue', 'pink', 'gray'])
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom')
    plt.title('Đánh giá hiệu quả tổng thể các thuật toán')
    plt.xlabel('Thuật toán')
    plt.ylabel('Điểm số')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'algorithm_score_bar.png' if from_game else 'algorithm_score_bar_final.png')
    plt.savefig(output_file)
    print(f"Biểu đồ điểm số tổng thể đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()
    ghost_names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
    algorithms = [metrics.get(ghost, {}).get('algorithm', 'Unknown') for ghost in ghost_names]
    step_counts = [metrics.get(ghost, {}).get('step_count', 0) for ghost in ghost_names]
    speeds = [metrics.get(ghost, {}).get('average_speed', 0) for ghost in ghost_names]
    efficiencies = [metrics.get(ghost, {}).get('path_efficiency', 0) for ghost in ghost_names]
    bar_width = 0.2
    index = np.arange(len(ghost_names))
    plt.figure(figsize=(12, 6))
    plt.bar(index - bar_width, step_counts, bar_width, label='Số bước', color='skyblue')
    plt.bar(index, speeds, bar_width, label='Tốc độ trung bình', color='lightgreen')
    plt.bar(index + bar_width, efficiencies, bar_width, label='Hiệu quả đường đi', color='salmon')
    for i, algo in enumerate(algorithms):
        plt.text(i, max(step_counts[i], speeds[i], efficiencies[i]) + 0.05, algo, ha='center', va='bottom', rotation=45)
    plt.xlabel('Ghost')
    plt.ylabel('Giá trị')
    plt.title('So sánh các chỉ số giữa các Ghost')
    plt.xticks(index, ghost_names)
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'ghost_metrics_grouped_bar.png' if from_game else 'ghost_metrics_grouped_bar_final.png')
    plt.savefig(output_file)
    print(f"Biểu đồ cột nhóm đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()
    plt.figure(figsize=(10, 6))
    plt.plot(ghost_names, step_counts, marker='o', label='Số bước', color='skyblue')
    plt.plot(ghost_names, speeds, marker='o', label='Tốc độ trung bình', color='lightgreen')
    plt.plot(ghost_names, efficiencies, marker='o', label='Hiệu quả đường đi', color='salmon')
    for i, algo in enumerate(algorithms):
        plt.text(i, step_counts[i] + 0.05, algo, ha='center', va='bottom', rotation=45)
    plt.title('Sự thay đổi của các chỉ số qua từng Ghost')
    plt.xlabel('Ghost')
    plt.ylabel('Giá trị')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'ghost_metrics_line.png' if from_game else 'ghost_metrics_line_final.png')
    plt.savefig(output_file)
    print(f"Biểu đồ đường đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()
    total_steps = sum(step_counts)
    if total_steps > 0:
        labels = [f"{ghost} ({algo})" for ghost, algo in zip(ghost_names, algorithms)]
        plt.figure(figsize=(8, 8))
        plt.pie(step_counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=['skyblue', 'lightgreen', 'salmon', 'lightblue'])
        plt.title('Tỷ lệ số bước di chuyển của các Ghost')
        plt.tight_layout()
        output_file = os.path.join(output_dir, 'step_count_pie.png' if from_game else 'step_count_pie_final.png')
        plt.savefig(output_file)
        print(f"Biểu đồ tròn đã được lưu vào {output_file}")
        if not from_game:
            plt.show()
        plt.close()
    plt.figure(figsize=(10, 6))
    unique_algos = list(set(algorithms))
    colors = ['skyblue', 'lightgreen', 'salmon', 'lightblue', 'pink', 'gray']
    algo_to_color = {algo: colors[i % len(colors)] for i, algo in enumerate(unique_algos)}
    for i, ghost in enumerate(ghost_names):
        algo = algorithms[i]
        plt.scatter(speeds[i], efficiencies[i], s=100, color=algo_to_color[algo], label=algo if i == algorithms.index(algo) else "", alpha=0.7)
        plt.text(speeds[i] + 0.02, efficiencies[i] + 0.02, ghost, fontsize=9)
    plt.title('Mối quan hệ giữa Tốc độ trung bình và Hiệu quả đường đi')
    plt.xlabel('Tốc độ trung bình')
    plt.ylabel('Hiệu quả đường đi')
    plt.legend(title='Thuật toán')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'speed_efficiency_scatter.png' if from_game else 'speed_efficiency_scatter_final.png')
    plt.savefig(output_file)
    print(f"Biểu đồ phân tán đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()

def analyze_ghost_logs_from_file(log_filepath, from_game=False):
    """Phân tích file nhật ký di chuyển của ma và lưu kết quả."""
    try:
        if from_game:
            pygame.display.quit()
        data = load_ghost_log(log_filepath)
        if data:
            metrics = analyze_ghost_logs(data)
            comparison = compare_algorithms(metrics)
            scores = evaluate_algorithms(comparison)
            save_comparison_to_file(comparison)
            visualize_evaluation(scores, metrics, from_game=from_game)
    except Exception as e:
        print(f"Lỗi khi phân tích nhật ký: {e}")
    if not from_game:
        pygame.quit()
        sys.exit()
    else:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        return True

if __name__ == "__main__":
    log_files = glob.glob("log/ghost_movement_log_*.json")
    if log_files:
        latest_file = max(log_files, key=os.path.getmtime)
        analyze_ghost_logs_from_file(latest_file, from_game=False)
    else:
        print("Không tìm thấy file nhật ký nào trong thư mục log/")