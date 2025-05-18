import os
import time
import struct
import gc
import matplotlib.pyplot as plt
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from aes_gcm_iot import AesGcmEnhanced


def save_results_to_file(std_time, enh_time, std_hr_time, enh_hr_time, std_workout_time, enh_workout_time):
    """Save the benchmark results to a text file"""
    with open('Results/smartwatch_real_world_results.txt', 'w') as f:
        f.write("=== SMARTWATCH DAILY OPERATION SIMULATION RESULTS ===\n\n")

        # Overall Results
        f.write("--- Overall Performance Results ---\n")
        f.write(f"Standard implementation: {std_time:.2f} ms\n")
        f.write(f"Enhanced implementation: {enh_time:.2f} ms\n")

        improvement = ((std_time - enh_time) / std_time) * 100
        speedup = std_time / enh_time
        f.write(f"Improvement: {improvement:.1f}%\n")
        f.write(f"Speedup factor: {speedup:.2f}x faster\n\n")

        # Battery impact
        battery_factor = 0.001
        std_battery = std_time * battery_factor
        enh_battery = enh_time * battery_factor
        battery_saved = std_battery - enh_battery

        f.write("--- Estimated Battery Impact ---\n")
        f.write(f"Standard implementation: {std_battery:.3f} units\n")
        f.write(f"Enhanced implementation: {enh_battery:.3f} units\n")
        f.write(f"Battery saved: {battery_saved:.3f} units ({(battery_saved / std_battery) * 100:.1f}%)\n\n")

        # Workload Analysis
        f.write("--- Workload Analysis ---\n\n")

        # Heart Rate Monitoring
        f.write("1. Continuous Heart Rate Monitoring (24 hours):\n")
        hr_improvement = ((std_hr_time - enh_hr_time) / std_hr_time) * 100
        f.write(f"Standard: {std_hr_time:.2f} ms, Enhanced: {enh_hr_time:.2f} ms\n")
        f.write(f"Improvement: {hr_improvement:.1f}%\n")
        f.write(f"Speedup: {std_hr_time / enh_hr_time:.2f}x faster\n\n")

        # Fitness Tracking
        f.write("2. Intensive Fitness Tracking (1 hour workout):\n")
        workout_improvement = ((std_workout_time - enh_workout_time) / std_workout_time) * 100
        f.write(f"Standard: {std_workout_time:.2f} ms, Enhanced: {enh_workout_time:.2f} ms\n")
        f.write(f"Improvement: {workout_improvement:.1f}%\n")
        f.write(f"Speedup: {std_workout_time / enh_workout_time:.2f}x faster\n\n")



    print(f"\nResults saved to 'smartwatch_real_world_results.txt'")


def visualize_results(std_time, enh_time, std_hr_time, enh_hr_time, std_workout_time, enh_workout_time):
    """Create visualizations of the benchmark results"""
    # Set up the figure
    plt.figure(figsize=(15, 10))
    plt.suptitle("Smartwatch Daily Operation Simulation Results", fontsize=16)

    # 1. Overall performance comparison
    plt.subplot(2, 2, 1)
    labels = ['Standard', 'Enhanced']
    times = [std_time, enh_time]
    x = np.arange(len(labels))
    width = 0.5

    bars = plt.bar(x, times, width, color=['#ff9999', '#66b3ff'])
    plt.xlabel('Implementation')
    plt.ylabel('Execution Time (ms)')
    plt.title('Overall Performance Comparison')
    plt.xticks(x, labels)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01*max(times),
                f"{height:.1f} ms", ha='center', va='bottom')

    improvement = ((std_time - enh_time) / std_time) * 100
    plt.text(0.5, times[0] * 0.5, f"{improvement:.1f}% Improvement",
             ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    plt.ylim(0, max(times) * 1.15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.subplot(2, 2, 2)
    categories = ['Heart Rate\nMonitoring', 'Fitness\nTracking']
    std_times = [std_hr_time, std_workout_time]
    enh_times = [enh_hr_time, enh_workout_time]

    x = np.arange(len(categories))
    width = 0.35

    plt.bar(x - width/2, std_times, width, label='Standard', color='#ff9999')
    plt.bar(x + width/2, enh_times, width, label='Enhanced', color='#66b3ff')

    plt.xlabel('Workload Type')
    plt.ylabel('Execution Time (ms)')
    plt.title('Performance by Workload Type')
    plt.xticks(x, categories)
    plt.legend()

    plt.ylim(0, max(std_times + enh_times) * 1.15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 3. Speedup factor comparison
    plt.subplot(2, 2, 3)
    speedups = [std_time/enh_time, std_hr_time/enh_hr_time, std_workout_time/enh_workout_time]
    labels = ['Overall', 'Heart Rate', 'Fitness']
    colors = ['#66b3ff', '#99ff99', '#ffcc99']

    bars = plt.bar(labels, speedups, color=colors)
    plt.xlabel('Scenario')
    plt.ylabel('Speedup Factor (x)')
    plt.title('Performance Speedup Factors')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                f"{height:.2f}x", ha='center', va='bottom')

    plt.ylim(0, max(speedups) * 1.15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 4. Battery impact visualization
    plt.subplot(2, 2, 4)

    # Assuming encryption operations take 0.001 units of battery per ms
    battery_factor = 0.001
    std_battery = std_time * battery_factor
    enh_battery = enh_time * battery_factor
    saved = std_battery - enh_battery

    # Create a stacked bar for the enhanced implementation
    plt.bar(['Battery Usage'], [enh_battery], label='Enhanced Usage', color='#66b3ff')
    plt.bar(['Battery Usage'], [saved], bottom=[enh_battery], label='Saved', color='#99ff99')

    # Add a marker for standard implementation
    plt.plot(['Battery Usage'], [std_battery], 'ro', markersize=10, label='Standard Usage')

    # Add text for the percentage saved - position it properly
    saving_percent = (saved / std_battery) * 100
    plt.text(0, std_battery * 0.7, f"{saving_percent:.1f}% Saved", ha='center',
             bbox=dict(facecolor='white', alpha=0.8))

    # Set y-axis limit to be just a bit higher than the standard battery usage
    plt.ylim(0, std_battery * 1.15)
    plt.ylabel('Battery Units')
    plt.title('Estimated Battery Impact')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Use tight_layout with appropriate padding
    plt.tight_layout(rect=[0, 0, 1, 0.95], pad=1.5)
    plt.savefig('smartwatch_real_world_results.png', dpi=300, bbox_inches='tight')
    print("\nVisualization saved as 'smartwatch_real_world_results.png'")
    plt.show()


def simulate_smartwatch_day():
    """
    Simulate a full day of smartwatch operation with both implementations.
    This represents a more realistic scenario than isolated benchmarks.
    """
    print("\n=== SMARTWATCH DAILY OPERATION SIMULATION ===")
    print("Simulating a full day of typical smartwatch usage")

    # Key for both implementations (128-bit for IoT devices)
    key_size = 128
    key = os.urandom(key_size // 8)

    # Prepare enhanced implementation
    enhanced = AesGcmEnhanced(key_size=key_size, persistent_iv=True)
    enhanced.set_key(key)

    # Define typical operations per day
    # Based on actual smartwatch usage patterns:
    heart_rate_readings = 24 * 60  # Every minute for 24 hours
    step_count_updates = 24 * 12  # Every 5 minutes
    sleep_tracking_points = 8 * 12  # During 8 hours of sleep, every 5 minutes
    fitness_activities = 4  # 4 workout sessions
    notification_encryptions = 40  # Messages, emails, etc.

    print(f"Operations to perform:")
    print(f"- Heart rate monitoring: {heart_rate_readings} readings")
    print(f"- Step count updates: {step_count_updates} updates")
    print(f"- Sleep tracking: {sleep_tracking_points} data points")
    print(f"- Fitness activities: {fitness_activities} sessions")
    print(f"- Notifications: {notification_encryptions} messages")

    total_operations = (heart_rate_readings + step_count_updates + sleep_tracking_points +
                        fitness_activities + notification_encryptions)
    print(f"Total operations: {total_operations}")

    # Generate sample data
    current_time = int(time.time())

    # Heart rate data (small, frequent)
    heart_data = []
    for i in range(heart_rate_readings):
        # Simulate realistic heart rate patterns
        hour = (i // 60) % 24
        if 0 <= hour < 6:  # Sleeping hours
            hr = 50 + (i % 10)  # Lower during sleep
        elif 6 <= hour < 8 or 18 <= hour < 22:  # Morning/evening activity
            hr = 70 + (i % 15)  # Moderate
        else:
            hr = 65 + (i % 25)  # Normal with variation
        heart_data.append(f"heartrate:{hr},timestamp:{current_time + i * 60}".encode())

    # Step count data
    step_data = []
    for i in range(step_count_updates):
        hour = (i // 12) % 24
        if 0 <= hour < 6:  # Sleeping hours
            steps = 0
        elif 6 <= hour < 9 or 17 <= hour < 20:  # Morning/evening activity
            steps = 1000 + (i % 500)
        else:
            steps = 500 + (i % 300)
        total_steps = i * steps // 10  # Accumulated steps
        step_data.append(f"steps:{total_steps},timestamp:{current_time + i * 300}".encode())

    # Sleep data (medium size, less frequent)
    sleep_data = []
    for i in range(sleep_tracking_points):
        stage = ["deep", "light", "rem", "awake"][i % 4]
        movement = i % 10
        sleep_data.append(
            f"sleep:stage={stage},movement={movement},hr={50 + (i % 10)},timestamp:{current_time + i * 300}".encode())

    # Fitness data (larger size, infrequent)
    fitness_data = []
    activities = ["running", "cycling", "walking", "gym"]
    for i in range(fitness_activities):
        activity = activities[i % len(activities)]
        duration = 30 + (i * 10)  # Minutes
        calories = 200 + (i * 50)
        distance = 3.0 + (i * 1.5)
        # Include GPS coordinates for each minute of activity (makes it larger)
        coords = ";".join([f"{37.7749 + i * 0.0001},{-122.4194 + i * 0.0001}" for i in range(duration)])
        data = f"activity:{activity},duration:{duration},calories:{calories},distance:{distance},gps:{coords}".encode()
        fitness_data.append(data)

    # Notification data (medium size, sporadic)
    notification_data = []
    for i in range(notification_encryptions):
        app = ["email", "sms", "messenger", "whatsapp", "calendar"][i % 5]
        length = 50 + (i % 100)  # Message length
        payload = os.urandom(length)  # Simulate encrypted message content
        notification_data.append(
            f"notification:app={app},timestamp={current_time + i * 1200},payload={str(payload)}".encode())

    # Run simulation with standard implementation
    print("\nRunning with standard implementation...")
    gc.collect()  # Force garbage collection before timing

    start_time = time.perf_counter()

    # Heart rate processing
    for data in heart_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    # Step count processing
    for data in step_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    # Sleep data processing
    for data in sleep_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    # Fitness data processing
    for data in fitness_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    # Notification processing
    for data in notification_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    end_time = time.perf_counter()
    std_time = (end_time - start_time) * 1000  # ms

    # Run simulation with enhanced implementation
    print("Running with enhanced implementation...")
    gc.collect()  # Force garbage collection before timing

    start_time = time.perf_counter()

    # Heart rate processing
    for data in heart_data:
        iv, ciphertext, tag = enhanced.encrypt(data)

    # Step count processing
    for data in step_data:
        iv, ciphertext, tag = enhanced.encrypt(data)

    # Sleep data processing
    for data in sleep_data:
        iv, ciphertext, tag = enhanced.encrypt(data)

    # Fitness data processing
    for data in fitness_data:
        iv, ciphertext, tag = enhanced.encrypt(data)

    # Notification processing
    for data in notification_data:
        iv, ciphertext, tag = enhanced.encrypt(data)

    end_time = time.perf_counter()
    enh_time = (end_time - start_time) * 1000  # ms

    # Report results
    print("\n--- Results ---")
    print(f"Standard implementation: {std_time:.2f} ms")
    print(f"Enhanced implementation: {enh_time:.2f} ms")

    improvement = ((std_time - enh_time) / std_time) * 100
    print(f"Improvement: {improvement:.1f}%")
    speedup = std_time / enh_time
    print(f"Speedup factor: {speedup:.2f}x faster")

    # Battery impact simulation
    # Assuming encryption operations take 0.001 units of battery per ms
    battery_factor = 0.001
    std_battery = std_time * battery_factor
    enh_battery = enh_time * battery_factor
    battery_saved = std_battery - enh_battery

    print(f"\nEstimated battery impact:")
    print(f"Standard implementation: {std_battery:.3f} units")
    print(f"Enhanced implementation: {enh_battery:.3f} units")
    print(f"Battery saved: {battery_saved:.3f} units ({(battery_saved / std_battery) * 100:.1f}%)")

    # Additional analysis for specific workloads
    print("\n--- Workload Analysis ---")

    # Continuous heart rate monitoring scenario
    # In this scenario, we simulate 24 hours of heart rate monitoring only
    print("\n1. Continuous Heart Rate Monitoring (24 hours):")

    # Standard implementation
    start_time = time.perf_counter()
    for data in heart_data:
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
    end_time = time.perf_counter()
    std_hr_time = (end_time - start_time) * 1000

    # Enhanced implementation
    start_time = time.perf_counter()
    for data in heart_data:
        iv, ciphertext, tag = enhanced.encrypt(data)
    end_time = time.perf_counter()
    enh_hr_time = (end_time - start_time) * 1000

    hr_improvement = ((std_hr_time - enh_hr_time) / std_hr_time) * 100
    print(f"Standard: {std_hr_time:.2f} ms, Enhanced: {enh_hr_time:.2f} ms")
    print(f"Improvement: {hr_improvement:.1f}%")
    print(f"Speedup: {std_hr_time / enh_hr_time:.2f}x faster")

    # Intensive fitness tracking scenario (longer data, higher frequency)
    print("\n2. Intensive Fitness Tracking (1 hour workout):")
    # Generate 60 minutes of second-by-second workout data
    workout_data = []
    for i in range(3600):  # 60 minutes * 60 seconds
        hr = 120 + (i % 40)  # Elevated heart rate
        cadence = 75 + (i % 10)
        lat = 37.7749 + (i * 0.00001)
        lon = -122.4194 + (i * 0.00001)
        data = f"workout:hr={hr},cadence={cadence},lat={lat},lon={lon},timestamp={current_time + i}".encode()
        workout_data.append(data)

    # Standard implementation
    start_time = time.perf_counter()
    for i, data in enumerate(workout_data):
        if i % 60 == 0:  # Simulate 1 reading per minute for this test
            iv = os.urandom(12)
            encryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            ).encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag
    end_time = time.perf_counter()
    std_workout_time = (end_time - start_time) * 1000

    # Enhanced implementation
    start_time = time.perf_counter()
    for i, data in enumerate(workout_data):
        if i % 60 == 0:  # Simulate 1 reading per minute for this test
            iv, ciphertext, tag = enhanced.encrypt(data)
    end_time = time.perf_counter()
    enh_workout_time = (end_time - start_time) * 1000

    workout_improvement = ((std_workout_time - enh_workout_time) / std_workout_time) * 100
    print(f"Standard: {std_workout_time:.2f} ms, Enhanced: {enh_workout_time:.2f} ms")
    print(f"Improvement: {workout_improvement:.1f}%")
    print(f"Speedup: {std_workout_time / enh_workout_time:.2f}x faster")

    visualize_results(std_time, enh_time, std_hr_time, enh_hr_time, std_workout_time, enh_workout_time)

    save_results_to_file(std_time, enh_time, std_hr_time, enh_hr_time, std_workout_time, enh_workout_time)

    return std_time, enh_time


if __name__ == "__main__":
    print("Simulating real-world smartwatch AES-GCM usage...")
    simulate_smartwatch_day()