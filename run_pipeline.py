import subprocess
import sys

steps = [
    "src/transform/clean_payments.py",
    "src/validation/validate_payments.py",
    "src/load/load_payments.py",
    "src/load/export_payment_summary.py"
]

for step in steps:
    print(f"\nRunning: {step}")

    result = subprocess.run(
        [sys.executable, step],
        check=True
    )

print("\nPipeline completed successfully.")