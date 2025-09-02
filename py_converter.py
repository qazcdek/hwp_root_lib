import subprocess
import os
import platform
import glob
import sys
import orjson
from typing import List

ROOT = os.path.abspath(os.path.dirname(__file__))

def _sep():
    return ';' if platform.system() == 'Windows' else ':'

def _run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed with code {r.returncode}: {' '.join(cmd)}")

def _find_cli_dir():
    # converterCLI 우선, 없으면 convertorCLI 폴백
    for name in ("converterCLI", "convertorCLI"):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p):
            return p
    raise FileNotFoundError("converterCLI 또는 convertorCLI 디렉터리를 찾을 수 없습니다.")

def _pick_one(patterns):
    cands = []
    for pat in patterns:
        cands.extend(glob.glob(pat))
    # -sources/-javadoc/original- 제외
    cands = [p for p in cands if p.endswith(".jar")
             and "-sources" not in p and "-javadoc" not in p and "original-" not in p]
    if not cands:
        raise FileNotFoundError(f"JAR을 찾지 못했습니다: {patterns}")
    with_deps = [p for p in cands if "with-dependencies" in os.path.basename(p)]
    return with_deps[0] if with_deps else max(cands, key=os.path.getmtime)

def _ensure_cli_compiled(cli_dir):
    # javac -d build 로 컴파일된 산출물 사용
    build_dir = os.path.join(cli_dir, "build")
    main_class_file = os.path.join(build_dir, "HwpxConverterCLI.class")

    if os.path.isfile(main_class_file):
        return build_dir  # 이미 컴파일됨

    # JAR 경로
    hwp2hwpx_jar = _pick_one([os.path.join(ROOT, "hwp_server", "hwp2hwpx", "target", "*.jar")])
    hwplib_jar   = _pick_one([os.path.join(ROOT, "hwp_server", "hwplib",   "target", "*.jar")])
    hwpxlib_jar  = _pick_one([os.path.join(ROOT, "hwp_server", "hwpxlib",  "target", "*.jar")])

    # 컴파일
    os.makedirs(build_dir, exist_ok=True)
    cp = _sep().join([hwp2hwpx_jar, hwplib_jar, hwpxlib_jar, "."])

    java_files = [f for f in os.listdir(cli_dir) if f.endswith(".java")]
    if "HwpxConverterCLI.java" not in java_files:
        raise FileNotFoundError(f"{cli_dir} 에 HwpxConverterCLI.java가 없습니다.")

    _run(["javac", "-encoding", "UTF-8", "-d", "build", "-cp", cp] + java_files, cwd=cli_dir)

    if not os.path.isfile(main_class_file):
        raise RuntimeError("컴파일 성공 후에도 HwpxConverterCLI.class를 찾지 못했습니다.")
    return build_dir

def convert_hwp_to_text(hwp_path: str | List[str]) -> str:
    """
    Java 기반 HwpxConverterCLI를 호출하여 .hwp/.hwpx 파일을 텍스트(JSON chunks)로 변환
    """
    if isinstance(hwp_path, str):
        hwp_path_list = [hwp_path]
    else:
        hwp_path_list = hwp_path
    
    total_result = []

    for hwp_path in hwp_path_list:
        if not os.path.exists(hwp_path):
            raise FileNotFoundError(f"입력 파일이 없습니다: {hwp_path}")

        cli_dir   = _find_cli_dir()
        build_dir = _ensure_cli_compiled(cli_dir)

        # JAR 경로
        hwp2hwpx_jar = _pick_one([os.path.join(ROOT, "hwp_server", "hwp2hwpx", "target", "*.jar")])
        hwplib_jar   = _pick_one([os.path.join(ROOT, "hwp_server", "hwplib",   "target", "*.jar")])
        hwpxlib_jar  = _pick_one([os.path.join(ROOT, "hwp_server", "hwpxlib",  "target", "*.jar")])

        classpath = _sep().join([build_dir, hwp2hwpx_jar, hwplib_jar, hwpxlib_jar])

        cmd = ["java", "-Dfile.encoding=UTF-8", "-cp", classpath, "HwpxConverterCLI", hwp_path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if proc.returncode != 0:
            # 디버깅에 도움되는 정보 출력
            print("❌ 변환 실패")
            print("stderr:\n" + proc.stderr)
            raise RuntimeError(f"Java returned {proc.returncode}")

        # STDERR에는 푸터 페이지번호 메타 로그가 있을 수 있으니 참고용으로 찍어도 됨
        if proc.stderr:
            print(proc.stderr, end="")

        # [수정] orjson으로 파싱하기 전에, Java의 원본 출력물을 확인합니다.
        print("--- Java stdout (raw output) ---")
        print(proc.stdout)
        print("---------------------------------")

        try:
            total_result.append(proc.stdout)
        except Exception as e: # FileNotFoundError에서 더 일반적인 Exception으로 변경
            print(f"❌ JSON 파싱 오류 또는 파일 시스템 오류 (오류 발생 파일을 건너뜁니다): {hwp_path}", file=sys.stderr)
            print(e, file=sys.stderr)
            continue # 다음 파일로 이동
        
    return total_result

# 사용 예시
if __name__ == "__main__":
    hwp_file = r"/data/qazcde/kiat/storage/hwp_dir/산업기술혁신사업 관련 법령 및 규정-3교.hwp"
    try:
        converted_text = convert_hwp_to_text(hwp_file)
        # print(type(converted_text)) # dict
        print(converted_text)
        print(len(converted_text))
    except Exception as e:
        print("에러:", e)
        sys.exit(1)