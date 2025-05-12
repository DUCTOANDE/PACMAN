import json
import os
import matplotlib.pyplot as plt
import numpy as np
import glob
import pygame
import sys
from .constants import *

def load_ghost_log(filepath):
    """Đọc dữ liệu từ file nhật ký ghost."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
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
        total_time = (end_time - start_time) / 1000.0 if end_time > start_time else 1.0
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
            'total_distance': total_distance,
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
                'avg_distance': 0,
                'avg_path_efficiency': 0,
                'instances': 0
            }
        comparison[algorithm]['ghosts'].append(ghost_name)
    for algorithm, data in comparison.items():
        ghosts = data['ghosts']
        if not ghosts:
            continue
        total_step_count = sum(metrics[ghost]['step_count'] for ghost in ghosts)
        total_distance = sum(metrics[ghost]['total_distance'] for ghost in ghosts)
        total_efficiency = sum(metrics[ghost]['path_efficiency'] for ghost in ghosts)
        count = len(ghosts)
        comparison[algorithm]['avg_step_count'] = total_step_count / count
        comparison[algorithm]['avg_distance'] = total_distance / count
        comparison[algorithm]['avg_path_efficiency'] = total_efficiency / count
        comparison[algorithm]['instances'] = count
    return comparison

def evaluate_algorithms(comparison):
    """Đánh giá tổng thể các thuật toán dựa trên các chỉ số đã chuẩn hóa."""
    scores = {}
    for algorithm, stats in comparison.items():
        if stats['avg_distance'] == 0 or stats['avg_step_count'] == 0:
            score = 0
        else:
            efficiency_score = stats['avg_path_efficiency'] * 50
            inverse_distance_score = (1 / stats['avg_distance']) * 30
            inverse_step_score = (1 / stats['avg_step_count']) * 20
            score = efficiency_score + inverse_distance_score + inverse_step_score
        scores[algorithm] = round(score, 2)
    return scores

def save_comparison_to_file(comparison):
    """Lưu kết quả so sánh vào file."""
    try:
        with open('algorithm_comparison.json', 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=4, ensure_ascii=False)
        print("Kết quả so sánh đã được lưu vào algorithm_comparison.json")
    except Exception as e:
        print(f"Lỗi khi lưu so sánh: {e}")

def visualize_evaluation(scores, metrics, from_game=True):
    """Trực quan hóa đánh giá các thuật toán bằng ba biểu đồ."""
    output_dir = "log"
    os.makedirs(output_dir, exist_ok=True)

    ghost_names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
    ghost_colors = {
        'Blinky': '#FF0000',
        'Inky': '#00FFFF',
        'Pinky': '#FFC0CB',
        'Clyde': '#FFA500'
    }

    step_counts = [metrics.get(ghost, {}).get('step_count', 0) for ghost in ghost_names]
    total_distances = [metrics.get(ghost, {}).get('total_distance', 0) for ghost in ghost_names]
    algorithms = [metrics.get(ghost, {}).get('algorithm', 'Unknown') for ghost in ghost_names]
    bar_colors = [ghost_colors.get(ghost, '#CCCCCC') for ghost in ghost_names]

    # Biểu đồ 1: Số bước
    plt.figure(figsize=(10, 6))
    bars = plt.bar(ghost_names, step_counts, color=bar_colors)
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{int(yval)}\n{algorithms[i]}',
                 ha='center', va='bottom', fontsize=10)
    plt.title('Số bước di chuyển của các Ghost', fontsize=16)
    plt.xlabel('Ghost', fontsize=13)
    plt.ylabel('Số bước', fontsize=13)
    plt.ylim(0, max(step_counts) * 1.15)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'ghost_step_count_bar.png' if from_game else 'ghost_step_count_bar_final.png')
    plt.savefig(output_file, dpi=120)
    print(f"Biểu đồ số bước đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()

    # Biểu đồ 2: Tổng khoảng cách
    plt.figure(figsize=(10, 6))
    bars = plt.bar(ghost_names, total_distances, color=bar_colors)
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, f'{yval:.1f}\n{algorithms[i]}',
                 ha='center', va='bottom', fontsize=10)
    plt.title('Tổng khoảng cách di chuyển của các Ghost', fontsize=16)
    plt.xlabel('Ghost', fontsize=13)
    plt.ylabel('Khoảng cách (pixel)', fontsize=13)
    plt.ylim(0, max(total_distances) * 1.15)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'ghost_distance_bar.png' if from_game else 'ghost_distance_bar_final.png')
    plt.savefig(output_file, dpi=120)
    print(f"Biểu đồ khoảng cách đã được lưu vào {output_file}")
    if not from_game:
        plt.show()
    plt.close()

    # Biểu đồ 3: Pie Chart hiệu quả
    labels = list(scores.keys())
    sizes = [max(0.01, score) for score in scores.values()]
    total_score = sum(sizes)
    explode = [0.1 if score == max(sizes) else 0 for score in sizes]

    def format_label(i):
        percent = sizes[i] / total_score * 100
        return f"{labels[i]} ({sizes[i]:.1f}) - {percent:.1f}%"

    formatted_labels = [format_label(i) for i in range(len(labels))]
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=formatted_labels, colors=colors,
            autopct='', shadow=True, startangle=90, textprops={'fontsize': 10})
    plt.title('Hiệu quả tổng thể của các thuật toán (Score)', fontsize=15, pad=20)
    plt.axis('equal')
    output_file = os.path.join(output_dir, 'algorithm_efficiency_pie.png' if from_game else 'algorithm_efficiency_pie_final.png')
    plt.savefig(output_file, dpi=120)
    print(f"Biểu đồ tròn hiệu quả đã được lưu vào {output_file}")
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
