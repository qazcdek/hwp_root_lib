import subprocess
import os
import platform
cwd = os.path.dirname(__file__)
classpath_elements = [
    os.path.join(cwd, "convertorCLI"),
    os.path.join(cwd, "hwp_server/hwp2hwpx/target/hwp2hwpx-1.0.0.jar"),
    os.path.join(cwd, "hwp_server/hwplib/target/hwplib-1.1.10.jar"),
    os.path.join(cwd, "hwp_server/hwpxlib/target/hwpxlib-1.0.5.jar")
]
def convert_hwp_to_text(hwp_path: str, classpath_elements: list[str] = classpath_elements) -> str:
    """
    Java 기반 HwpxConverterCLI를 호출하여 .hwp/.hwpx 파일을 텍스트로 변환

    :param hwp_path: HWP or HWPX 파일 전체 경로
    :param classpath_elements: jar 파일 또는 디렉터리 경로 리스트
    :return: 추출된 텍스트 결과
    """
    # 운영체제에 따라 classpath 구분자 선택
    separator = ';' if platform.system() == 'Windows' else ':'
    classpath = separator.join(classpath_elements)

    cmd = [
        "java",
        "-cp",
        classpath,
        "HwpxConverterCLI",
        hwp_path
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print("❌ 변환 실패:", e.stderr)
        raise

# 사용 예시
if __name__ == "__main__":
    hwp_file = r"C:\Users\Admin\Desktop\i_bricks\code_space\test_space\storage\hwp_dir\real_01.hwp"  # 또는 Windows 경로
    converted_text = convert_hwp_to_text(hwp_file)
    print(converted_text)