import subprocess
import os
import platform
import glob
import sys
from typing import List

ROOT = os.path.abspath(os.path.dirname(__file__))

def run(cmd, cwd=None):
    print(f"🛠 {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed with code {r.returncode}: {' '.join(cmd)}")

def sep():
    return ';' if platform.system() == 'Windows' else ':'

def find_cli_dir():
    # converterCLI 우선, 없으면 convertorCLI 폴백
    for name in ("converterCLI", "convertorCLI"):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p):
            print("cli 찾음")
            print(p)
            print("cli 찾음")
            return p
    raise FileNotFoundError("converterCLI 또는 convertorCLI 디렉터리를 찾을 수 없습니다.")

def pick_one(patterns):
    cands = []
    for pat in patterns:
        cands.extend(glob.glob(pat))
    # -sources/-javadoc 제외
    cands = [p for p in cands if p.endswith(".jar")
             and "-sources" not in p and "-javadoc" not in p and "original-" not in p]
    if not cands:
        raise FileNotFoundError(f"JAR을 찾지 못했습니다: {patterns}")
    # jar-with-dependencies가 있으면 우선
    with_deps = [p for p in cands if "with-dependencies" in os.path.basename(p)]
    return with_deps[0] if with_deps else max(cands, key=os.path.getmtime)

def ensure_cli_compiled(cli_dir, force_recompile=False):
    main_class_file = os.path.join(cli_dir, "HwpxConverterCLI.class")
    
    # force_recompile 플래그가 False이고 클래스 파일이 존재하면 재컴파일 건너뛰기
    if os.path.isfile(main_class_file) and not force_recompile:
        return cli_dir

    # JAR 경로 탐색 (컴파일에 필요)
    hwp2hwpx_jar = pick_one([
        os.path.join(ROOT, "hwp_server", "hwp2hwpx", "target", "*.jar")
    ])
    hwplib_jar = pick_one([
        os.path.join(ROOT, "hwp_server", "hwplib", "target", "*.jar")
    ])
    hwpxlib_jar = pick_one([
        os.path.join(ROOT, "hwp_server", "hwpxlib", "target", "*.jar")
    ])

    # 컴파일
    os.makedirs(cli_dir, exist_ok=True)
    cp = sep().join([hwp2hwpx_jar, hwplib_jar, hwpxlib_jar, "."])

    java_files = [f for f in os.listdir(cli_dir) if f.endswith(".java")]
    if "HwpxConverterCLI.java" not in java_files:
        raise FileNotFoundError(f"{cli_dir} 에 HwpxConverterCLI.java가 없습니다.")

    run(["javac", "-encoding", "UTF-8", "-cp", cp] + java_files, cwd=cli_dir)
    if not os.path.isfile(main_class_file):
        print(main_class_file)
        raise RuntimeError("컴파일은 성공했지만 HwpxConverterCLI.class를 찾지 못했습니다.")
    return cli_dir

def reinstall_java_dependencies():
    """
    Maven 라이브러리와 자바 CLI를 순서대로 재설치합니다.
    """
    print("🚀 Java 의존성 재설치를 시작합니다...")

    # 1. hwplib 재설치
    hwplib_path = os.path.join(ROOT, "hwp_server", "hwplib")
    run(["mvn", "clean", "install", "-DskipTests"], cwd=hwplib_path)

    # 2. hwpxlib 재설치
    hwpxlib_path = os.path.join(ROOT, "hwp_server", "hwpxlib")
    run(["mvn", "clean", "install", "-DskipTests"], cwd=hwpxlib_path)

    # 3. hwp2hwpx 재설치
    hwp2hwpx_path = os.path.join(ROOT, "hwp_server", "hwp2hwpx")
    run(["mvn", "clean", "install", "-DskipTests"], cwd=hwp2hwpx_path)

    # 4. HwpxConverterCLI 재컴파일
    cli_dir = find_cli_dir()
    ensure_cli_compiled(cli_dir, force_recompile=True)
    print("✅ 모든 Java 의존성 및 CLI 재설치 완료.")


def convert_hwp_to_text(hwp_path: str) -> str:
    """
    Java 기반 HwpxConverterCLI를 호출하여 .hwp/.hwpx를 JSON 텍스트로 변환
    """
    cli_dir = find_cli_dir()
    build_dir = ensure_cli_compiled(cli_dir) # 재설치 시 force=True 옵션이 없으므로, 이미 컴파일된 CLI를 사용

    # JAR 경로
    hwp2hwpx_jar = pick_one([os.path.join(ROOT, "hwp_server", "hwp2hwpx", "target", "*.jar")])
    hwplib_jar   = pick_one([os.path.join(ROOT, "hwp_server", "hwplib", "target", "*.jar")])
    hwpxlib_jar  = pick_one([os.path.join(ROOT, "hwp_server", "hwpxlib", "target", "*.jar")])

    classpath = sep().join([build_dir, hwp2hwpx_jar, hwplib_jar, hwpxlib_jar])

    cmd = ["java", "-cp", classpath, "HwpxConverterCLI", hwp_path]
    print(f"▶ 실행: {' '.join(cmd)}")
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        # 디버깅에 도움되는 정보 출력
        print("❌ 변환 실패")
        print("stderr:\n" + r.stderr)
        raise RuntimeError(f"Java returned {r.returncode}")
    return r.stdout

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'reinstall':
        reinstall_java_dependencies()
    else:
        # 사용 예시
        hwp_file = "/data/qazcde/kiat/storage/hwp_dir/real_01.hwp"
        try:
            out = convert_hwp_to_text(hwp_file)
            print(out)
        except Exception as e:
            print("에러:", e)
            sys.exit(1)