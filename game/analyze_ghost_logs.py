import json
import os
import time
import matplotlib.pyplot as plt
from collections import defaultdict
import glob
import matplotlib.patches as mpatches
from matplotlib import font_manager

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

# Trực quan hóa cải tiến với hiển thị tuần tự
def visualize_evaluation(scores):
    if not scores:
        print("Không có dữ liệu để trực quan hóa")
        return

    algos = list(scores.keys())
    total_scores = [scores[algo]['total_score'] for algo in algos]
    steps = [scores[algo]['steps'] for algo in algos]
    avg_distances = [scores[algo]['avg_distance'] for algo in algos]
    direction_changes = [scores[algo]['direction_changes'] for algo in algos]

    # Thiết lập phong cách và font
    plt.style.use('ggplot')
    try:
        font_manager.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        plt.rcParams['font.family'] = 'DejaVu Sans'
    except:
        plt.rcParams['font.family'] = 'sans-serif'

    # Màu sắc gradient
    colors = ['#1abc9c' if score == max(total_scores) else '#e74c3c' if score == min(total_scores) else '#2980b9' for score in total_scores]
    timestamp = time.strftime("%Y%m%d_%H%M%S")



    # Biểu đồ 1: Số bước
    fig2 = plt.figure(figsize=(10, 8))
    bars = plt.bar(algos, steps, color=colors, edgecolor='black', alpha=0.9)
    plt.title('Số bước di chuyển', fontsize=20, pad=20, fontweight='bold')
    plt.ylabel('Số bước', fontsize=16)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    for bar, value in zip(bars, steps):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(steps)*0.03, 
                 f'{value:.1f}', ha='center', fontsize=14, fontweight='bold', color='black')
    avg_steps = sum(steps) / len(steps) if steps else 0
    plt.axhline(avg_steps, color='#8e44ad', linestyle='--', linewidth=2, label=f'Trung bình: {avg_steps:.1f}')
    plt.legend(fontsize=12, frameon=True)
    plt.xlabel('Thuật toán', fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.gca().set_facecolor('#f5f6fa')
    fig2.savefig(os.path.join('log_analysis_results', f'steps_{timestamp}.png'), dpi=300, bbox_inches='tight')
    plt.show()  # Đợi người dùng đóng cửa sổ

    # Biểu đồ 2: Khoảng cách trung bình
    fig3 = plt.figure(figsize=(10, 8))
    bars = plt.bar(algos, avg_distances, color=colors, edgecolor='black', alpha=0.9)
    plt.title('Khoảng cách trung bình đến người chơi', fontsize=20, pad=20, fontweight='bold')
    plt.ylabel('Khoảng cách (Manhattan)', fontsize=16)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    for bar, value in zip(bars, avg_distances):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_distances)*0.03, 
                 f'{value:.2f}', ha='center', fontsize=14, fontweight='bold', color='black')
    avg_distance = sum(avg_distances) / len(avg_distances) if avg_distances else 0
    plt.axhline(avg_distance, color='#8e44ad', linestyle='--', linewidth=2, label=f'Trung bình: {avg_distance:.2f}')
    plt.legend(fontsize=12, frameon=True)
    plt.xlabel('Thuật toán', fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.gca().set_facecolor('#f5f6fa')
    fig3.savefig(os.path.join('log_analysis_results', f'distance_{timestamp}.png'), dpi=300, bbox_inches='tight')
    plt.show()  # Đợi người dùng đóng cửa sổ

    # Biểu đồ 3: Số lần thay đổi hướng
    fig4 = plt.figure(figsize=(10, 8))
    bars = plt.bar(algos, direction_changes, color=colors, edgecolor='black', alpha=0.9)
    plt.title('Số lần thay đổi hướng', fontsize=20, pad=20, fontweight='bold')
    plt.ylabel('Số lần thay đổi', fontsize=16)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    for bar, value in zip(bars, direction_changes):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(direction_changes)*0.03, 
                 f'{value:.1f}', ha='center', fontsize=14, fontweight='bold', color='black')
    avg_changes = sum(direction_changes) / len(direction_changes) if direction_changes else 0
    plt.axhline(avg_changes, color='#8e44ad', linestyle='--', linewidth=2, label=f'Trung bình: {avg_changes:.1f}')
    plt.legend(fontsize=12, frameon=True)
    plt.xlabel('Thuật toán', fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.gca().set_facecolor('#f5f6fa')
    fig4.savefig(os.path.join('log_analysis_results', f'direction_changes_{timestamp}.png'), dpi=300, bbox_inches='tight')
    plt.show()  # Đợi người dùng đóng cửa sổ
    
    # Biểu đồ 4: Tổng điểm
    fig1 = plt.figure(figsize=(10, 8))
    bars = plt.bar(algos, total_scores, color=colors, edgecolor='black', alpha=0.9)
    plt.title('Tổng điểm các thuật toán', fontsize=20, pad=20, fontweight='bold')
    plt.ylabel('Điểm (0-100)', fontsize=16)
    plt.ylim(0, 120)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    for bar, score in zip(bars, total_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, f'{score:.1f}', 
                 ha='center', fontsize=14, fontweight='bold', color='black')
    best_patch = mpatches.Patch(color='#1abc9c', label='Thuật toán tối ưu')
    worst_patch = mpatches.Patch(color='#e74c3c', label='Thuật toán kém tối ưu')
    normal_patch = mpatches.Patch(color='#2980b9', label='Bình thường')
    plt.legend(handles=[best_patch, worst_patch, normal_patch], fontsize=12, loc='upper right', frameon=True)
    plt.xlabel('Thuật toán', fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.gca().set_facecolor('#f5f6fa')
    fig1.savefig(os.path.join('log_analysis_results', f'total_score_{timestamp}.png'), dpi=300, bbox_inches='tight')
    plt.show()  # Đợi người dùng đóng cửa sổ

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
            for algo, count in metric['algorithm_counts'].items():
                print(f"    {algo}: {count} bước")

        comparison = compare_algorithms(metrics)

        print("\nSo sánh các thuật toán:")
        for algo, comp in comparison.items():
            print(f"\n{algo}:")
            print(f"  Tổng số bước: {comp['steps']:.2f}")
            print(f"  Khoảng cách trung bình đến người chơi: {comp['avg_distance']:.2f}")
            print(f"  Số lần thay đổi hướng: {comp['direction_changes']:.2f}")

        save_comparison_to_file(comparison)

        choice = input("Bạn có muốn trực quan hóa kết quả so sánh? (y/n): ")
        if choice.lower() == 'y':
            scores = evaluate_algorithms(comparison)
            visualize_evaluation(scores)

if __name__ == "__main__":
    try:
        import matplotlib.pyplot
    except ImportError:
        print("Lỗi: Thư viện matplotlib chưa được cài đặt. Cài đặt bằng: pip install matplotlib")
    else:
        main_analysis()