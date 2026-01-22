# 라이브러리 배포 가이드

이 문서는 xls-template-renderer를 독립 라이브러리로 배포하는 방법을 설명합니다.

## PyPI 배포

### 1. 사전 준비

```bash
# 빌드 도구 설치
pip install build twine

# PyPI 계정 생성
# https://pypi.org/account/register/
```

### 2. 버전 업데이트

`pyproject.toml`과 `src/xls_template_renderer/__init__.py`의 버전을 업데이트합니다:

```toml
# pyproject.toml
[project]
version = "0.2.0"
```

```python
# __init__.py
__version__ = "0.2.0"
```

### 3. 빌드

```bash
# 빌드 디렉토리 정리
rm -rf dist/

# 패키지 빌드
python -m build
```

빌드 후 `dist/` 디렉토리에 다음 파일이 생성됩니다:
- `xls_template_renderer-0.2.0.tar.gz` (소스 배포판)
- `xls_template_renderer-0.2.0-py3-none-any.whl` (휠)

### 4. TestPyPI에서 테스트 (선택사항)

```bash
# TestPyPI에 업로드
twine upload --repository testpypi dist/*

# TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ xls-template-renderer
```

### 5. PyPI 업로드

```bash
twine upload dist/*
```

### 6. 설치 확인

```bash
pip install xls-template-renderer
```

## 프라이빗 패키지 서버

사내 배포용으로 프라이빗 패키지 서버를 사용할 수 있습니다.

### Artifactory / Nexus

```bash
# .pypirc 설정
[distutils]
index-servers =
    internal

[internal]
repository = https://your-server.com/repository/pypi/
username = your-username
password = your-password

# 업로드
twine upload --repository internal dist/*
```

### 직접 설치 (Git)

```bash
pip install git+https://github.com/your-org/xls-template-renderer.git
```

## GitHub Releases

### 1. 태그 생성

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### 2. GitHub Release 생성

1. GitHub 저장소의 Releases 페이지로 이동
2. "Draft a new release" 클릭
3. 태그 선택 및 릴리스 노트 작성
4. 빌드된 파일 첨부 (선택사항)

### 3. GitHub Actions 자동 배포

`.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## 버전 관리 전략

### Semantic Versioning

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환 기능 추가
- **PATCH**: 하위 호환 버그 수정

### 예시

- `0.1.0`: 초기 개발 버전
- `0.1.1`: 버그 수정
- `0.2.0`: 새 기능 추가 (예: elif 지원)
- `1.0.0`: 안정 버전 릴리스

## 체크리스트

배포 전 확인사항:

- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 버전 번호 업데이트
- [ ] CHANGELOG 업데이트
- [ ] README 업데이트
- [ ] 라이선스 파일 확인
- [ ] 의존성 버전 확인

## 의존성 관리

### 최소 버전 지정

```toml
[project]
dependencies = [
    "openpyxl>=3.1.0",
]
```

### 버전 고정 (선택사항)

개발 환경 재현을 위해:

```bash
pip freeze > requirements-lock.txt
```

## 문서화

### Read the Docs 연동

1. `docs/` 디렉토리에 Sphinx 문서 작성
2. `.readthedocs.yml` 설정 파일 추가
3. Read the Docs에 프로젝트 등록

### mkdocs 사용

```bash
pip install mkdocs mkdocs-material
mkdocs new .
mkdocs serve  # 로컬 미리보기
mkdocs gh-deploy  # GitHub Pages 배포
```
