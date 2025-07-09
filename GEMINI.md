# PDF 논문 한글 번역 가이드

> **번역 안내:**
> - 한글 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어로 그대로 표기합니다.
> - 문장 구조와 설명은 자연스러운 한글로 번역하되, 용어와 논문 제목, figure/table의 caption(설명문)은 영어로 유지합니다.
> - 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성합니다.

## 🏃‍♂️ 빠른 시작 (Quick Start)

1. PDF 텍스트 추출, 한글 번역, 자동 디렉토리 및 파일 저장
   ```
   <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어 그대로 사용하고, 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성해줘.
   ```

---

## 📚 단계별 상세 가이드

### 1. PDF 파일 경로 확인
- 번역할 PDF 파일의 전체 경로를 확인합니다. (예: `/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf`)

### 2. PDF 텍스트 추출, 번역, 자동 디렉토리 및 파일 저장
- 아래 프롬프트에서 `<PDF_FILE_PATH>`를 실제 경로로 바꿔 입력합니다.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어 그대로 사용하고, 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성해줘.
  ```
  - **이미지(figure) 작성법:**
    - 논문 내 이미지는 아래와 같이 작성합니다.
        ```html
        <figure><img src="assets/Figure_3.png" alt="Figure 3"><figcaption><p>Figure 3: ...</p></figcaption></figure>
        ```
      - figure의 caption(설명문)은 영어 원문 그대로 유지합니다.
      - img의 src는 "assets/" 디렉토리 하위의 이미지(.png) 파일을 사용하며, 이미지 이름은 캡션의 이름(예: "Figure 3" → "Figure_3.png")으로 하고, 띄워쓰기는 언더바(_)로 변경합니다.
      - img의 alt는 캡션의 이름(예: "Figure 3")으로 합니다.
  - **표(table) 작성법:**
    - 논문 본문에 표가 등장하면 반드시 마크다운 테이블(`| 헤더 | ... |`) 형식으로 작성합니다.
      ```markdown
      | 모델 | BLEU (EN-DE) | BLEU (EN-FR) |
      |------|--------------|--------------|
      | Transformer | 28.4 | 41.8 |
      ```
    - 표(table)의 caption(설명문)도 영어 원문 그대로 유지합니다.
  - **마지막 단계 체크리스트:**
    - 번역이 끝난 후, 본문과 참고문헌 뒤에 추가 데이터(figure, table, appendix 등)가 누락되지 않았는지 반드시 확인합니다.
    - 누락된 데이터가 있다면 모두 번역 결과에 포함합니다.

### 3. 논문 제목 추출 및 디렉토리 생성
  ```
  <PDF_FILE_PATH> 파일의 제목을 추출해줘.
  "추출된 제목"으로 디렉토리를 만들어줘. 공백은 하이픈으로 바꾸고 모두 소문자로 만들어줘.
  ```

### 4. 전문 용어 유지 번역
- 번역 시 특정 용어를 영어로 남기고 싶을 때는 아래와 같이 요청합니다.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어 그대로 사용해줘.
  ```

### 5. 참고문헌 처리 안내
- 논문 번역 시 반드시 References(참고문헌) 섹션을 포함합니다.
- 본문 내 참고문헌 인용 번호는 `[[1]](#ref1)`, `[[2]](#ref2)`와 같이, 각 번호가 하단 참고문헌 항목의 앵커와 정확히 연결되도록 마크다운 링크를 사용합니다.
  - 예시 (본문): `이 방법은 기존 연구[[1]](#ref1)와 비교하여 ...`
- 하단 참고문헌 항목은 반드시 마크다운 리스트(- 또는 *) 형태로 작성하며, 각 번호별로 앵커를 추가해 본문 인용과 연결합니다.
  - 예시 (하단): `- <a id="ref1"></a>[1] Lei Ba et al. Layer normalization. [arXiv:1607.06450](https://arxiv.org/abs/1607.06450)`
  - 마크다운 리스트 예시:
    ```markdown
    - <a id="ref1"></a>[1] Lei Ba et al. Layer normalization. [arXiv:1607.06450](https://arxiv.org/abs/1607.06450)
    - <a id="ref2"></a>[2] Vaswani et al. Attention is all you need. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
    ```
- 각 참고문헌 항목은 논문 제목을 영어 원문 그대로 표기합니다.
- 공식, DOI, arXiv 등 실제 논문 URL을 찾아 마크다운 링크로 추가합니다.
- 참고문헌 번호는 본문 내 인용([1], [2], ...)과 일치해야 하며, 번호는 그대로 사용합니다.

---

## 💡 실전 예시 (Best Practice)

```
/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf 에 있는 논문을 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘.
```

- **이미지(figure) 작성법:**
  - 반드시 아래와 같은 형태로 작성합니다.
    ```html
    <figure><img src="assets/Figure_3.png" alt="Figure 3"><figcaption><p>Figure 3: ...</p></figcaption></figure>
    ```
  - caption(설명문)은 영어 원문 그대로 유지합니다.
  - img의 src는 "assets/" 디렉토리 하위의 이미지(.png) 파일을 사용하며, 이미지 이름은 캡션의 이름(예: "Figure 3" → "Figure_3.png")으로 하고, 띄워쓰기는 언더바(_)로 변경합니다.
  - img의 alt는 캡션의 이름(예: "Figure 3")으로 합니다.

- **표(table) 작성법:**
  - 반드시 마크다운 테이블(`| 헤더 | ... |`) 형식으로 작성합니다.
    ```markdown
    | 모델 | BLEU (EN-DE) | BLEU (EN-FR) |
    |------|--------------|--------------|
    | Transformer | 28.4 | 41.8 |
    ```

- **수식 작성법:**
  - GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성합니다.
    - 예시 (인라인): `Attention score는 $e_{ij} = a(q_i, k_j)$로 계산합니다.`
    - 예시 (블록):
      ```latex
      $$
      \text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}
      $$
      ```

- **참고문헌(References) 작성법:**
  - 논문 마지막에 반드시 References(참고문헌) 섹션을 포함합니다.
  - 본문 내 참고문헌 인용 번호는 `[[1]](#ref1)`, `[[2]](#ref2)`와 같이, 각 번호가 하단 참고문헌 항목의 앵커와 정확히 연결되도록 마크다운 링크를 사용합니다.
    - 예시 (본문): `이 방법은 기존 연구[[1]](#ref1)와 비교하여 ...`
  - 하단 참고문헌 항목은 반드시 마크다운 리스트(- 또는 *) 형태로 작성하며, 각 번호별로 앵커를 추가해 본문 인용과 연결합니다.
    - 예시 (하단): `- <a id="ref1"></a>[1] Lei Ba et al. Layer normalization. [arXiv:1607.06450](https://arxiv.org/abs/1607.06450)`
    - 마크다운 리스트 예시:
      ```markdown
      - <a id="ref1"></a>[1] Lei Ba et al. Layer normalization. [arXiv:1607.06450](https://arxiv.org/abs/1607.06450)
      - <a id="ref2"></a>[2] Vaswani et al. Attention is all you need. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
      ```
  - 각 참고문헌 항목은 논문 제목을 영어 원문 그대로 표기합니다.
  - 공식, DOI, arXiv 등 실제 논문 URL을 찾아 마크다운 링크로 추가합니다.
  - 참고문헌 번호는 본문 내 인용([1], [2], ...)과 일치해야 하며, 번호는 그대로 사용합니다.

---

### ✅ 번역 및 저장 후 최종 체크리스트
- 본문, 표(table), 그림(figure), 수식, 부록(appendix) 등 모든 데이터가 번역 결과에 포함되어 있는지 확인합니다.
- 번역 결과가 논문 제목 디렉토리의 README.md에 자동 저장되었는지 확인합니다.
- 번역 결과가 자연스럽고 이해할 수 있는 수준인지, 어색하거나 이상한 부분이 없는지 검토합니다.
- 해당 디렉토리에 기존 README.md 파일이 있다면, 새 번역 내용이 누락 없이 반영되었는지, 기존 내용과 병합 또는 업데이트가 필요한 부분이 없는지 반드시 확인하고 필요시 업데이트합니다.

---

이 가이드는 논문 번역 및 관리 자동화를 위한 실전 프롬프트 예시와 고급 활용법을 제공합니다. 필요에 따라 각 섹션의 프롬프트를 조합해 사용할 수 있습니다.
