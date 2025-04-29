import json
import os
import time
import matplotlib.pyplot as plt
from collections import defaultdict
import glob
import matplotlib.patches as mpatches
from matplotlib import font_manager
import pygame

# Đọc file JSON log
def load_ghost_log(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file log tại '{file_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Lỗi: File log '{file_path}' không phải JSON hợp lệ")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc file '{file_path}': {e}")
        return None

# Tính khoảng cách Manhattan
def manhattan_distance(pos1, pos2):
    try:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    except (TypeError, IndexError):
        return float('inf')

# Phân tích log của các con ma
def analyze_ghost_logs(data):
    metrics = defaultdict(lambda: {
        'steps': 0,
        'direction_changes': 0,
        'distances': [],
        'algorithm_counts': defaultdict(int)
    })

    if not data:
        print("Lỗi: Dữ liệu log trống hoặc không hợp lệ")
        return dict(metrics)

    player_pos = [6, 6]  # Giả sử vị trí người chơi cố định

    for ghost_name, ghost_data in data.items():
        movements = ghost_data.get('movements', [])
        if not movements:
            print(f"Cảnh báo: Không có dữ liệu di chuyển cho {ghost_name}")
            continue

        prev_direction = None
        for move in movements:
            algorithm = move.get('algorithm')
            grid_pos = move.get('grid_pos')
            direction = move.get('direction')

            if not grid_pos or direction is None or algorithm is None:
                print(f"Cảnh báo: Bước di chuyển không hợp lệ cho {ghost_name}: {move}")
                continue

            if algorithm not in ['Initial', 'Reset']:
                metrics[ghost_name]['steps'] += 1
                metrics[ghost_name]['algorithm_counts'][algorithm] += 1

            if prev_direction is not None and direction != prev_direction:
                metrics[ghost_name]['direction_changes'] += 1
            prev_direction = direction

            distance = manhattan_distance(grid_pos, player_pos)
            if distance != float('inf'):
                metrics[ghost_name]['distances'].append(distance)

        distances = metrics[ghost_name]['distances']
        metrics[ghost_name]['avg_distance'] = sum(distances) / len(distances) if distances else 0.0

    return dict(metrics)

# So sánh các thuật toán
def compare_algorithms(metrics):
    comparison = {
        'A*': {'steps': 0, 'avg_distance': 0, 'direction_changes': 0, 'count': 0},
        'Dijkstra': {'steps': 0, 'avg_distance': 0, 'direction_changes': 0, 'count': 0},
        'BFS': {'steps': 0, 'avg_distance': 0, 'direction_changes': 0, 'count': 0},
        'Random': {'steps': 0, 'avg_distance': 0, 'direction_changes': 0, 'count': 0}
    }

    for ghost_name, metric in metrics.items():
        total_steps = metric['steps']
        if total_steps == 0:
            print(f"Cảnh báo: {ghost_name} không có bước di chuyển hợp lệ")
            continue

        if ghost_name == 'Blinky':
            algo = 'A*'
        elif ghost_name == 'Inky':
            algo = 'Dijkstra'
        elif ghost_name == 'Clyde':
            algo = 'BFS'
        elif ghost_name == 'Pinky':
            for algo, count in metric['algorithm_counts'].items():
                if algo in ['A*', 'Random']:
                    ratio = count / total_steps if total_steps > 0 else 0
                    comparison[algo]['steps'] += metric['steps'] * ratio
                    comparison[algo]['avg_distance'] += metric['avg_distance'] * ratio
                    comparison[algo]['direction_changes'] += metric['direction_changes'] * ratio
                    comparison[algo]['count'] += ratio
            continue
        else:
            continue

        comparison[algo]['steps'] += metric['steps']
        comparison[algo]['avg_distance'] += metric['avg_distance']
        comparison[algo]['direction_changes'] += metric['direction_changes']
        comparison[algo]['count'] += 1

    for algo in comparison:
        if comparison[algo]['count'] > 0:
            comparison[algo]['avg_distance'] /= comparison[algo]['count']
        else:
            comparison[algo]['avg_distance'] = 0
            print(f"Cảnh báo: Thuật toán {algo} không được sử dụng (count=0)")

    return comparison

# Lưu kết quả so sánh vào file JSON
def save_comparison_to_file(comparison, log_dir="log_analysis_results"):
    try:
        os.makedirs(log_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(log_dir, f"algorithm_comparison_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=4, ensure_ascii=False)
        print(f"Đã lưu kết quả so sánh vào: {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu file so sánh: {e}")

# Đánh giá thuật toán
def evaluate_algorithms(comparison):
    max_steps = max(comp['steps'] for comp in comparison.values() if comp['steps'] > 0) or 1
    max_distance = max(comp['avg_distance'] for comp in comparison.values() if comp['avg_distance'] > 0) or 1
    max_changes = max(comp['direction_changes'] for comp in comparison.values() if comp['direction_changes'] > 0) or 1

    scores = {}
    for algo, comp in comparison.items():
        step_score = 100 * (1 - comp['steps'] / max_steps) if comp['steps'] > 0 else 0
        distance_score = 100 * (1 - comp['avg_distance'] / max_distance) if comp['avg_distance'] > 0 else 0
        change_score = 100 * (1 - comp['direction_changes'] / max_changes) if comp['direction_changes'] > 0 else 0
        total_score = (step_score + distance_score + change_score) / 3

        scores[algo] = {
            'steps': comp['steps'],
            'avg_distance': comp['avg_distance'],
            'direction_changes': comp['direction_changes'],
            'total_score': total_score
        }

    return scores

# Trực quan hóa cải tiến
def visualize_evaluation(scores, from_game=False):
    if not scores:
        print("Không có dữ liệu để trực quan hóa")
        return

    algos = list(scores.keys())
    valid_algos = [algo for algo in algos if scores[algo]['steps'] > 0 or scores[algo]['avg_distance'] > 0 or scores[algo]['direction_changes'] > 0 or scores[algo]['total_score'] > 0]
    if not valid_algos:
        print("Không có dữ liệu hợp lệ để trực quan hóa sau khi lọc.")
        return

    algos = valid_algos
    total_scores = [scores[algo]['total_score'] for algo in algos]
    steps = [scores[algo]['steps'] for algo in algos]
    avg_distances = [scores[algo]['avg_distance'] for algo in algos]
    direction_changes = [scores[algo]['direction_changes'] for algo in algos]

    # Quyết định có hiển thị biểu đồ không (chỉ khi không gọi từ game)
    show_plots = False
    if not from_game:
        pygame.quit()  # Đóng Pygame trước khi hiển thị lời nhắc
        while True:
            choice = input("Bạn có muốn hiển thị các biểu đồ phân tích không? (y/n): ").strip().lower()
            if choice == 'y':
                show_plots = True
                print("Sẽ hiển thị các biểu đồ...")
                break
            else:
                print("Sẽ không hiển thị biểu đồ.")
                return
                

    else:
        print("Phân tích từ trò chơi: Chỉ lưu biểu đồ, không hiển thị.")

    # Thiết lập phong cách và font
    plt.style.use('ggplot')

    # Màu sắc gradient
    if total_scores:
        max_score_val = max(total_scores)
        min_score_val = min(total_scores)
        colors = ['#1abc9c' if score == max_score_val else '#e74c3c' if score == min_score_val else '#2980b9' for score in total_scores]
    else:
        colors = ['#2980b9'] * len(algos)

    # Danh sách các biểu đồ
    plots_config = [
        {
            'title': 'Số bước di chuyển',
            'data': steps,
            'ylabel': 'Số bước',
            'filename_base': 'steps',
            'format': '.1f',
            'avg': sum(steps) / len(steps) if steps else 0,
            'avg_label': 'Trung bình: {:.1f}'
        },
        {
            'title': 'Khoảng cách trung bình đến người chơi',
            'data': avg_distances,
            'ylabel': 'Khoảng cách (Manhattan)',
            'filename_base': 'distance',
            'format': '.2f',
            'avg': sum(avg_distances) / len(avg_distances) if avg_distances else 0,
            'avg_label': 'Trung bình: {:.2f}'
        },
        {
            'title': 'Số lần thay đổi hướng',
            'data': direction_changes,
            'ylabel': 'Số lần thay đổi',
            'filename_base': 'direction_changes',
            'format': '.1f',
            'avg': sum(direction_changes) / len(direction_changes) if direction_changes else 0,
            'avg_label': 'Trung bình: {:.1f}'
        },
        {
            'title': 'Tổng điểm các thuật toán',
            'data': total_scores,
            'ylabel': 'Điểm (0-100)',
            'filename_base': 'total_score',
            'format': '.1f',
            'avg': None,
            'ylim': (0, 120),
            'legend': [
                mpatches.Patch(color='#1abc9c', label='Thuật toán tối ưu'),
                mpatches.Patch(color='#e74c3c', label='Thuật toán kém tối ưu'),
                mpatches.Patch(color='#2980b9', label='Bình thường')
            ]
        }
    ]

    # Tạo và xử lý từng biểu đồ
    save_dir = 'log_analysis_results'
    os.makedirs(save_dir, exist_ok=True)

    for plot_info in plots_config:
        if not plot_info['data']:
            print(f"Bỏ qua biểu đồ '{plot_info['title']}' do không có dữ liệu.")
            continue

        fig = plt.figure(figsize=(8, 6))
        bars = plt.bar(algos, plot_info['data'], color=colors, edgecolor='black', alpha=0.9)
        plt.title(plot_info['title'], fontsize=16, pad=20, fontweight='bold')
        plt.ylabel(plot_info['ylabel'], fontsize=12)
        plt.xlabel('Thuật toán', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)
        plt.gca().set_facecolor('#f5f6fa')
        plt.tight_layout(pad=1.5)

        max_value = max(plot_info['data']) if plot_info['data'] else 1
        for bar, value in zip(bars, plot_info['data']):
            text_y = bar.get_height() + max_value * 0.02
            plt.text(bar.get_x() + bar.get_width()/2, text_y,
                     f'{value:{plot_info["format"]}}', ha='center', va='bottom',
                     fontsize=10, fontweight='bold', color='black')

        if plot_info.get('avg') is not None:
            plt.axhline(plot_info['avg'], color='#8e44ad', linestyle='--', linewidth=2, label=plot_info['avg_label'].format(plot_info['avg']))
            if 'legend' in plot_info:
                handles, labels = plt.gca().get_legend_handles_labels()
                handles.extend(plot_info['legend'])
                plt.legend(handles=handles, fontsize=10, loc='upper right', frameon=True)
            else:
                plt.legend(fontsize=10, frameon=True)
        elif 'legend' in plot_info:
            plt.legend(handles=plot_info['legend'], fontsize=10, loc='upper right', frameon=True)

        if 'ylim' in plot_info:
            plt.ylim(plot_info['ylim'])
        else:
            current_ylim = plt.gca().get_ylim()
            plt.ylim(current_ylim[0], current_ylim[1] * 1.1)

        # Lưu biểu đồ
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{plot_info['filename_base']}_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)
        try:
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Đã lưu biểu đồ vào: {filepath}")
        except Exception as e:
            print(f"Lỗi khi lưu biểu đồ {filename}: {e}")

        # Chỉ hiển thị biểu đồ nếu chạy độc lập và người dùng chọn 'y'
        if not from_game and show_plots:
            print(f"Hiển thị biểu đồ: {plot_info['title']}")
            plt.show()

        plt.close(fig)  # Đóng figure để giải phóng bộ nhớ

# Hàm chính
def main_analysis():
    log_dir = "log"
    if not os.path.isdir(log_dir):
        print(f"Lỗi: Thư mục '{log_dir}' không tồn tại")
        return

    log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
    if not log_files:
        print(f"Lỗi: Không tìm thấy file log nào trong '{log_dir}'")
        return

    latest_file = max(log_files, key=os.path.getmtime)
    print(f"Phân tích file log: {latest_file}")

    data = load_ghost_log(latest_file)
    if data:
        metrics = analyze_ghost_logs(data)

        print("\nPhân tích chỉ số theo con ma:")
        for ghost_name, metric in metrics.items():
            print(f"\n{ghost_name}:")
            print(f"  Tổng số bước: {metric['steps']}")
            print(f"  Khoảng cách trung bình đến người chơi: {metric['avg_distance']:.2f}")
            print(f"  Số lần thay đổi hướng: {metric['direction_changes']}")
            print("  Tần suất thuật toán:")
            if metric.get('algorithm_counts'):
                for algo, count in metric['algorithm_counts'].items():
                    print(f"    {algo}: {count} bước")
            else:
                print("    Không có dữ liệu tần suất thuật toán.")

        comparison = compare_algorithms(metrics)

        print("\nSo sánh các thuật toán:")
        for algo, comp in comparison.items():
            if comp.get('count', 0) > 0 or comp.get('steps', 0) > 0:
                print(f"\n{algo}:")
                print(f"  Tổng số bước (ước tính): {comp.get('steps', 0):.2f}")
                print(f"  Khoảng cách trung bình (ước tính): {comp.get('avg_distance', 0):.2f}")
                print(f"  Số lần thay đổi hướng (ước tính): {comp.get('direction_changes', 0):.2f}")
                print(f"  Tỷ lệ sử dụng (ước tính): {comp.get('count', 0):.2f}")
            else:
                print(f"\n{algo}: Không được sử dụng trong log này.")

        save_comparison_to_file(comparison)
        scores = evaluate_algorithms(comparison)

        print("\nĐánh giá điểm số thuật toán:")
        for algo, score_data in scores.items():
            if comparison.get(algo, {}).get('count', 0) > 0 or comparison.get(algo, {}).get('steps', 0) > 0:
                print(f"\n{algo}:")
                print(f"  Tổng điểm: {score_data['total_score']:.2f}")

        if scores:
            visualize_evaluation(scores, from_game=False)
        else:
            print("Không có điểm số để trực quan hóa.")

if __name__ == "__main__":
    main_analysis()