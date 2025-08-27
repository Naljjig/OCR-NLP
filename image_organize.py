import os
from pathlib import Path
import shutil
from PIL import Image
import imagehash
from collections import defaultdict
import time

def backup_folder(source_dir):
    # 백업 폴더 이름에 타임스탬프 추가
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_dir = f"{source_dir}_backup_{timestamp}"
    
    # 폴더 전체를 복사
    shutil.copytree(source_dir, backup_dir)
    print(f"백업 완료: {backup_dir}")
    return backup_dir

def restore_from_backup(backup_dir, target_dir):
    try:
        # 타겟 디렉토리의 모든 파일 삭제
        for file in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # 백업에서 모든 파일 복원
        for file in os.listdir(backup_dir):
            src_path = os.path.join(backup_dir, file)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, target_dir)
        
        print(f"복원 완료: {target_dir}")
        return True
    except Exception as e:
        print(f"복원 중 오류 발생: {e}")
        return False

def remove_duplicates(root_dir, create_backup=True):
    # 백업 생성
    backup_path = None
    if create_backup:
        backup_path = backup_folder(root_dir)
    
    # 지원하는 이미지 확장자
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # 이미지 해시값을 저장할 딕셔너리
    hash_dict = defaultdict(list)
    total_images = 0
    
    # 모든 이미지 파일 검사
    for file in os.listdir(root_dir):
        if file.lower().endswith(image_extensions):
            total_images += 1
            file_path = os.path.join(root_dir, file)
            try:
                # 이미지 해시값 계산
                with Image.open(file_path) as img:
                    hash_value = str(imagehash.average_hash(img))
                    hash_dict[hash_value].append(file_path)
            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {file_path}, 오류: {e}")
    
    # 중복 이미지 제거
    duplicates_removed = 0
    for hash_value, file_list in hash_dict.items():
        if len(file_list) > 1:  # 중복된 이미지가 있는 경우
            # 첫 번째 이미지는 유지하고 나머지는 삭제
            for file_path in file_list[1:]:
                os.remove(file_path)
                duplicates_removed += 1
    
    # 남은 이미지 파일 이름 재정리
    remaining_files = [f for f in os.listdir(root_dir) 
                      if f.lower().endswith(image_extensions)]
    
    for index, old_name in enumerate(sorted(remaining_files), start=1):
        old_path = os.path.join(root_dir, old_name)
        extension = os.path.splitext(old_name)[1]
        new_name = f"{index}{extension}"
        new_path = os.path.join(root_dir, new_name)
        os.rename(old_path, new_path)
    
    return total_images, total_images - duplicates_removed, backup_path

#def organize_images(root_dir):
    # 지원하는 이미지 확장자
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # 모든 이미지 파일의 경로를 저장할 리스트
    image_files = []
    
    # 재귀적으로 모든 하위 폴더 탐색
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                # 전체 파일 경로 생성
                file_path = os.path.join(root, file)
                image_files.append(file_path)
    
    # 메인 폴더 경로
    main_folder = Path(root_dir)
    
    # 각 이미지 파일을 메인 폴더로 이동하고 이름 변경
    for index, old_path in enumerate(image_files, start=1):
        # 파일 확장자 가져오기
        extension = os.path.splitext(old_path)[1]
        # 새로운 파일 이름 생성 (예: 1.jpg, 2.jpg, ...)
        new_filename = f"{index}{extension}"
        new_path = main_folder / new_filename
        
        # 파일이 이미 메인 폴더에 있지 않은 경우에만 이동
        if os.path.dirname(old_path) != str(main_folder):
            shutil.move(old_path, new_path)
        else:
            # 같은 폴더에 있는 경우 이름만 변경
            os.rename(old_path, new_path)
    
    print(f"총 {len(image_files)}개의 이미지 파일을 정리했습니다.")

if __name__ == "__main__":
    dir = "Dataset/dataset"
    
    # 중복 제거 (백업 생성과 함께)
    total, remaining, backup_path = remove_duplicates(dir, create_backup=True)
    print(f"\n중복 제거 결과:")
    print(f"처음 이미지 개수: {total}")
    print(f"중복 제거 후 이미지 개수: {remaining}")
    print(f"제거된 중복 이미지 개수: {total - remaining}")
    print(f"백업 경로: {backup_path}")
    
    # 복원이 필요한 경우 아래 코드의 주석을 해제하여 사용
    # restore_from_backup(backup_path, dir)
