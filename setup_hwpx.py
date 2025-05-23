import subprocess
import platform
import os

def run_command(cmd, cwd=None):
    print(f"🛠 실행: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        print("❌ 실패:", result.returncode)
        exit(1)

def main():
    root = os.path.abspath(os.path.dirname(__file__))
    separator = ';' if platform.system() == 'Windows' else ':'

    # 1. hwplib 설치
    run_command(["mvn", "clean", "install", "-DskipTests"], cwd=os.path.join(root, "hwp_server", "hwplib"))

    # 2. hwpxlib 설치
    run_command(["mvn", "clean", "install", "-DskipTests"], cwd=os.path.join(root, "hwp_server", "hwpxlib"))

    # 3. hwp2hwpx 설치
    run_command(["mvn", "clean", "install", "-DskipTests"], cwd=os.path.join(root, "hwp_server", "hwp2hwpx"))

    # 4. hwp_server는 선택 실행 (개발 서버 모드로 돌리려면 주석 해제)
    # run_command(["mvn", "clean", "compile", "quarkus:dev", "-Dquarkus.enforceBuildGoal=false"], cwd=os.path.join(root, "hwp_server"))

    # 5. HwpxConverterCLI 컴파일
    classpath = separator.join([
        ".",
        os.path.join("..", "hwp_server", "hwp2hwpx", "target", "hwp2hwpx-1.0.0.jar"),
        os.path.join("..", "hwp_server", "hwplib", "target", "hwplib-1.1.10.jar"),
        os.path.join("..", "hwp_server", "hwpxlib", "target", "hwpxlib-1.0.5.jar")
    ])
    java_files = [f for f in os.listdir(os.path.join(root, "convertorCLI")) if f.endswith(".java")]
    for java_file in java_files:
        run_command([
            "javac", "-cp", classpath, java_file
        ], cwd=os.path.join(root, "convertorCLI"))

    print("✅ 전체 빌드 완료!")

if __name__ == "__main__":
    main()
