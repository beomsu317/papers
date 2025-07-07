# PDF 논문 한글 번역 가이드

## 🏃‍♂️ 빠른 시작 (Quick Start)

1. **PDF 텍스트 추출, 한글 번역, 자동 디렉토리 및 파일 저장**
   ```
   <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘.
   ```

---

## 📚 단계별 상세 가이드

### 1. PDF 파일 경로 확인
- 번역할 PDF 파일의 전체 경로를 확인하세요. (예: `/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf`)

### 2. PDF 텍스트 추출, 번역, 자동 디렉토리 및 파일 저장
- 아래 프롬프트에서 `<PDF_FILE_PATH>`를 실제 경로로 바꿔 입력하세요.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘.
  ```
  - **이미지(figure) 부분 안내:**
    - 논문 내 이미지(figure)는 아래와 같이 `<figure><img src="" alt=""><figcaption><p>...</p></figcaption></figure>` 형태로 캡션을 달아줘.
    - **figure의 caption(설명문)은 번역하지 말고, 반드시 영어 원문 그대로 유지해줘.**
    - **img의 src는 빈 칸으로 두고 alt도 빈 칸으로 둬.**
    - 예시:
      ```html
      <figure><img src="" alt=""><figcaption><p>Figure 3: An example of the attention mechanism following long-distance dependencies in the encoder self-attention in layer 5 of 6. ...</p></figcaption></figure>
      ```
  - **표(table) 부분 안내:**
    - 논문 본문에 표가 등장하면 반드시 마크다운 테이블(`| 헤더 | ... |`) 형식으로 작성해줘.
    - 예시:
      ```markdown
      | 모델 | BLEU (EN-DE) | BLEU (EN-FR) |
      |------|--------------|--------------|
      | Transformer | 28.4 | 41.8 |
      ```
  - **마지막 단계 체크리스트:**
    - 번역이 끝난 후, 본문과 참고문헌 뒤에 추가 데이터(figure, table, appendix 등)가 누락되지 않았는지 반드시 확인해줘.
    - 누락된 데이터가 있다면 모두 번역 결과에 포함해줘.

### 3. 논문 제목만 추출 및 디렉토리 생성
  ```
  <PDF_FILE_PATH> 파일의 제목을 추출해줘.
  "추출된 제목"으로 디렉토리를 만들어줘. 공백은 하이픈으로 바꾸고 모두 소문자로 만들어줘.
  ```

### 4. 전문 용어 유지 번역
- 번역 시 특정 용어는 영어로 남기고 싶다면 아래처럼 요청하세요.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 의미가 모호해지거나 IT 전문 용어(예: Transformer, attention, model, layer)는 영어 그대로 사용해줘.
  ```

### 5. 참고문헌 링크 자동화
- 본문 내 참고번호([1], [5], [12-15] 등)는 참고문헌(References) 목록을 따로 작성하지 말고, 각 번호를 실제 논문 URL(예: DOI, arXiv, 공식 페이지 등)로 바로 마크다운 링크로 변환해서 본문에 삽입해줘.
- 참고문헌 항목별로 가능한 한 실제 논문 URL(공식, DOI, arXiv 등)을 찾아서 본문 내 번호에 직접 마크다운 링크로 연결해줘.
  ```
  본문에 있는 참고 번호(예: [1], [5], [12-15])를 참고문헌의 실제 논문 URL(예: DOI, arXiv, 공식 페이지 등)로 바로 마크다운 링크로 변환해서 본문에 삽입해줘. 참고문헌(References) 목록은 작성하지 않아도 돼.
  예를 들어, 본문의 [1]은 "[1](https://arxiv.org/abs/1706.03762)"처럼 실제 논문 URL로 연결되는 마크다운 링크가 되어야 해.
  ```

---

## 💡 실전 예시

```
/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf 에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘.
```

※ 이미지(figure) 부분은 아래와 같이 캡션을 포함한 figure 태그로 작성해줘. (caption은 반드시 영어 원문 그대로 유지, img의 src와 alt는 빈 칸)
<figure><img src="" alt=""><figcaption><p>Figure 3: ...</p></figcaption></figure>
※ 표(table) 부분은 반드시 마크다운 테이블 형식으로 작성해줘.

예시:
| 모델 | BLEU (EN-DE) | BLEU (EN-FR) |
|------|--------------|--------------|
| Transformer | 28.4 | 41.8 |

(번역 완료 후)
```
본문에 있는 참고 번호(예: [1], [5], [12-15])를 참고문헌의 실제 논문 URL(예: DOI, arXiv, 공식 페이지 등)로 바로 마크다운 링크로 변환해서 본문에 삽입해줘. 참고문헌(References) 목록은 작성하지 않아도 돼.

예시: [1](https://arxiv.org/abs/1706.03762)
```

---

이 가이드는 논문 번역 및 관리 자동화를 위한 실전 프롬프트 예시와 고급 활용법을 제공합니다. 필요에 따라 각 섹션의 프롬프트를 조합해 사용하세요.
