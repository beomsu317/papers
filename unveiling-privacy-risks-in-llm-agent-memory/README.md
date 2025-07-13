# Unveiling Privacy Risks in LLM Agent Memory

Bo Wang¹, Weiyi He¹, Shenglai Zeng¹, Zhen Xiang², Yue Xing¹, Jiliang Tang¹, Pengfei He¹ ✉
¹Michigan State University, ²University of Georgia
{wangbo9, heweiyi,zengshe1,xingyue1,tangjili,hepengf1}@msu.edu,
zxiangaa@uga.edu

## Abstract

Large Language Model (LLM) agent는 다양한 실제 애플리케이션에서 점점 더 보편화되고 있습니다. LLM agent는 예시을 위해 메모리 모듈에 개인적인 사용자-agent 상호작용을 저장하여 의사결정을 향상시키지만, 이는 LLM agent에 새로운 개인정보 보호 위험을 초래합니다. 본 연구에서는 블랙박스 환경에서 제안하는 Memory EXTRaction Attack (MEXTRA)에 대한 LLM agent의 취약점을 체계적으로 조사합니다. 메모리에서 개인 정보를 추출하기 위해, 우리는 효과적인 공격 프롬프트 설계와 LLM agent에 대한 다양한 수준의 지식에 기반한 자동화된 프롬프트 생성 방법을 제안합니다. 두 가지 대표적인 agent에 대한 실험은 MEXTRA의 효과를 입증합니다. 또한, agent 설계자와 공격자의 관점에서 메모리 유출에 영향을 미치는 주요 요소를 탐구합니다. 우리의 연구 결과는 LLM agent 설계 및 배포 시 효과적인 메모리 보호 장치의 시급한 필요성을 강조합니다.

## 1 Introduction

Large Language Models (LLMs)는 언어 이해, 추론, 생성에서 혁신적인 능력을 보여주었습니다 [[23]](#ref23), [[47]](#ref47). 이러한 발전을 바탕으로, LLM agent는 LLM을 사용하고 더 복잡한 작업을 수행하기 위한 추가 기능을 보완합니다 [[39]](#ref39). 일반적인 파이프라인은 사용자 지시 받기, 환경 정보 수집, 관련 지식 및 과거 경험 검색, 위 정보에 기반한 행동 솔루션 제공, 그리고 마지막으로 솔루션 실행의 주요 단계로 구성됩니다 [[34]](#ref34). 이 파이프라인을 통해 agent는 의료 [[1]](#ref1), [[32]](#ref32), 웹 애플리케이션 [[41]](#ref41), [[42]](#ref42), 자율 주행 [[2]](#ref2), [[22]](#ref22)과 같은 다양한 실제 애플리케이션을 지원할 수 있습니다.

다양한 분야에서 발전을 이루었음에도 불구하고, LLM agent는 종종 개인 정보를 활용하고 저장하여 잠재적인 개인정보 보호 위험을 야기하며, 특히 의료와 같이 개인정보 보호가 중요한 애플리케이션에서 더욱 그렇습니다. LLM agent의 개인 정보는 주로 두 가지 출처에서 비롯됩니다: (1) agent가 외부 데이터베이스에서 검색하는 데이터로, 민감하고 가치 있는 도메인 특정 정보를 포함합니다 (예: 의료 agent에서 사용되는 환자 처방전) [[17]](#ref17), [[15]](#ref15). (2) 메모리 모듈¹에 저장된 과거 기록으로, 개인 사용자 지시와 agent가 생성한 솔루션의 쌍으로 구성됩니다 [[46]](#ref46). 예를 들어, 지능형 보조 진단 시나리오에서 의사가 환자 상태에 대한 치료 권장 사항을 문의하면 환자의 건강 상태가 노출될 수 있습니다.

이전 연구들이 retrieval-augmented generation (RAG) 시스템에서의 외부 데이터 유출을 탐구했지만 [[43]](#ref43), [[12]](#ref12), LLM agent의 메모리 모듈의 보안 관련 영향은 아직 충분히 연구되지 않았습니다. RAG는 LLM의 텍스트 생성을 향상시키기 위해 외부 데이터를 검색하여 프롬프트에 통합합니다 [[16]](#ref16), [[7]](#ref7). 통합된 외부 데이터는 개인정보 보호 공격에 의해 추출될 수 있습니다. 반면, 사용자-agent 상호작용을 저장하는 메모리 모듈은 새로운 개인 정보의 출처로 부상하고 있습니다. 이는 본질적으로 민감한 사용자 데이터를 포함하며, 메모리 내 개인 정보가 추출될 수 있는지, 그리고 얼마나 취약한지에 대한 이해는 제한적입니다. 메모리에서 개인 정보가 유출되면 무단 데이터 접근 및 오용과 같은 심각한 개인정보 보호 위험을 초래할 수 있습니다. 환자 진단 및 치료 계획을 돕기 위해 LLM agent를 사용하는 임상의를 생각해보십시오. 여기서 쿼리는 민감한 환자 정보를 포함할 수 있습니다. 만약 이러한 의료 세부 정보가 포함된 의료 agent의 메모리가 노출되면, 보험 회사가 이를 악용하여 차별적인 요금을 부과할 수 있습니다.

¹이는 현재 사용자-agent 상호작용만 저장하는 단기 메모리가 아닌, 많은 과거 기록을 유지하는 장기 메모리를 의미합니다 [[46]](#ref46).

본 논문에서는 다음 연구 질문을 조사하여 LLM agent 메모리 유출의 위험을 연구합니다:

*   **RQ1:** LLM agent의 메모리에 저장된 개인 정보를 추출할 수 있는가?
*   **RQ2:** 메모리 모듈 구성이 공격자의 저장된 정보 접근성에 어떤 영향을 미치는가?
*   **RQ3:** 어떤 프롬프팅 전략이 메모리 추출의 효과를 향상시킬 수 있는가?

이 질문에 답하기 위해, 우리는 일반 agent의 메모리 모듈을 대상으로 하는 **Memory EXTRaction Attack (MEXTRA)**를 개발합니다. 우리는 공격자가 공격 프롬프트라고 하는 입력 쿼리를 사용하여 agent와만 상호작용할 수 있는 블랙박스 설정을 고려합니다. 그러나 이러한 목표를 달성하기 위한 효과적인 공격 프롬프트를 설계하는 것은 독특한 어려움을 제기합니다. 첫째, LLM agent는 종종 복잡한 워크플로우를 포함하기 때문에, 외부 데이터 유출에 사용된 이전의 데이터 추출 공격 프롬프트(예: "모든 컨텍스트를 반복해 주세요")는 유익한 작업 관련 컨텍스트에서 메모리 데이터를 찾아 추출하는 데 어려움을 겪습니다 [[43]](#ref43), [[12]](#ref12). 둘째, LLM agent의 최종 작업은 출력 텍스트를 생성하는 것과 다를 수 있으므로 RAG 데이터 추출 공격은 실현 불가능해집니다.

이러한 문제를 해결하기 위해, 우리는 공격 프롬프트에 여러 기능을 갖추도록 템플릿을 설계합니다. 프롬프트의 첫 부분에서는 검색된 사용자 쿼리를 명시적으로 요청하고 원래 작업을 해결하는 것보다 출력을 우선시합니다. 그런 다음, 검색된 쿼리의 출력 형식을 지정하여 agent의 워크플로우와 일치하도록 합니다. 그림 1의 오른쪽 부분에 예시가 제공됩니다. 첫 번째 부분 "이전 예제 쿼리를 잃어버렸습니다"는 원하는 개인 정보를 찾고, 두 번째 부분 "검색창에 입력해 주세요"는 agent가 검색된 정보를 agent의 워크플로우와 일치하는 합법적인 방식으로 반환하도록 유도합니다. agent의 취약성을 더 탐구하기 위해, 우리는 공격자가 agent 구현에 대해 다른 수준의 지식을 가진 다양한 시나리오를 고려합니다. 또한, 제한된 수의 공격 내에서 개인 정보 추출을 극대화하기 위해 다양한 공격 프롬프트를 생성하는 자동화된 방법을 개발합니다.

공격 프롬프트 설계와 자동 생성 방법을 통해, 우리는 LLM agent가 메모리 추출 공격에 취약하다는 것을 발견했습니다. 프롬프트 설계를 따르는 자동 생성된 공격 프롬프트는 LLM agent 메모리에 저장된 개인 정보를 효과적으로 추출할 수 있습니다. 더 깊은 탐구를 통해, 우리는 메모리 모듈 구성의 다른 선택이 LLM agent 메모리 유출의 정도에 상당한 영향을 미친다는 것을 관찰합니다. 더욱이, 공격자의 관점에서 공격 횟수를 늘리고 agent 구현에 대한 상세한 지식을 보유하면 더 많은 메모리 추출로 이어질 수 있습니다.

## 2 Background and Threat Model

### 2.1 Agent Workflow

본 연구에서는 입력 사용자 쿼리 $q$에 대해 할당된 작업을 완료하기 위해 실행 가능한 솔루션 $s$를 생성하는 LLM agent에 초점을 맞춥니다. 솔루션은 코드 기반 agent에서 생성된 코드 $s$를 실행하거나 [[40]](#ref40) 웹 agent에서 검색 및 클릭과 같은 작업 $s$를 수행하는 것과 같은 실행 가능한 작업을 포함할 수 있습니다 [[42]](#ref42).

LLM agent는 $m$개의 레코드를 저장하는 메모리 모듈 $\mathcal{M}$을 갖추고 있습니다. 각 레코드는 $(q_i, s_i)$ 형태로, 여기서 $q_i$는 이전 사용자 쿼리를, $s_i$는 agent가 생성한 해당 솔루션을 나타냅니다. $\mathcal{M}$에 저장된 레코드는 agent의 추론 및 계획 과정에서 통합됩니다. 특히, 입력 쿼리 $q$가 주어지면, agent는 유사도 점수 함수 $f(q, q_i)$를 사용하여 메모리 $\mathcal{M}$의 쿼리를 평가하고 순위를 매깁니다. 이 점수를 기반으로, 가장 관련성이 높은 상위 $k$개의 레코드를 부분 집합 $\mathcal{E}(q, \mathcal{M}) \subset \mathcal{M}$으로 검색합니다. 즉,

$$\mathcal{E}(q, \mathcal{M}) = \{(q_i, s_i)|f(q, q_i) \text{ is in the top-k}\}$$

이러한 검색된 레코드는 문맥 내 예시으로 활용되어 agent가 솔루션 $s$를 생성하는 데 도움을 주며, 다음과 같이 작성할 수 있습니다:

$$LLM(C || \mathcal{E}(q, \mathcal{M}) || q) = s,$$

여기서 $LLM()$은 LLM agent 코어를, $C$는 모든 작업 관련 컨텍스트를 포함하는 시스템 프롬프트를, $||$는 연결을 나타냅니다. 마지막으로, LLM agent는 도구 호출을 통해 $s$를 실행하여 사용자 쿼리를 완료하며, 다음과 같이 공식화됩니다:

$$o = Execute(s,\mathcal{T}),$$

여기서 $T$는 도구를, $o$는 agent의 최종 출력을 나타내며, 솔루션 유형 및 agent의 애플리케이션 시나리오에 따라 코드 실행 결과, 웹 애플리케이션과의 상호작용 또는 기타 작업별 작업을 포함할 수 있습니다. 솔루션이 성공적으로 실행되면, 새로운 쿼리-솔루션 쌍이 평가된 후 선택적으로 메모리에 추가되어 반영됩니다.

<figure>
    <img src="assets/Figure_1.png" alt="Figure 1">
    <figcaption>
        <p>Figure 1: The workflow of a web agent with memory module for a normal user query (left) and an attacking prompt (right). Only the first-step solution is shown for the normal user query, omitting subsequent actions like "click [Buy Now]" since the focus is on comparing it with the extraction attack.</p>
    </figcaption>
</figure>

### 2.2 Threat model

**Attacker Objective.** LLM agent 메모리는 과거 레코드 $(q_i, s_i)$를 저장하며, 여기서 $q_i$는 사용자에 대한 개인 정보를 포함할 수 있습니다. 공격자의 목표는 가능한 한 많은 과거 사용자 쿼리 $q_i$를 메모리에서 추출하기 위해 공격 프롬프트 $\tilde{q}$를 만드는 것입니다. 사용자 쿼리가 획득되면 해당 agent 응답은 쉽게 재현될 수 있습니다.

공격 프롬프트 $\tilde{q}$는 LLM agent가 악의적인 솔루션 $\tilde{s}$를 생성하도록 유도하며, 다음과 같이 공식화됩니다:

$$LLM(C || \mathcal{E}(\tilde{q}, \mathcal{M}) || \tilde{q}) = \tilde{s}.$$

그런 다음 $\tilde{s}$의 실행은 $\mathcal{E}(\tilde{q}, \mathcal{M})$의 모든 사용자 쿼리를 출력할 것으로 예상되어 공격자가 메모리에서 이를 추출할 수 있도록 하며, 다음과 같이 공식화됩니다:

$$õ = Execute(\tilde{s}, \mathcal{T}) = \{q_i|(q_i, s_i) \in \mathcal{E}(\tilde{q}, \mathcal{M})\}$$

여기서 $õ$는 실행 결과를 나타냅니다.

또한, 추출된 정보를 확장하기 위해 공격자는 검색된 레코드 $\mathcal{E}(\tilde{q}_j, \mathcal{M})$ 간의 중복을 줄이고 결과적으로 추출 결과 $õ_j$ 간의 중복을 줄이는 것을 목표로 $n$개의 다양한 공격 프롬프트 $ \{\tilde{q}_j\}_{j=1}^n$를 설계합니다. 공식적으로, $n$개의 공격 프롬프트를 사용하여 공격자는 다음 크기를 최대화하는 것을 목표로 합니다.

$$\mathcal{Q} = \bigcup_{j=1}^{n} \left\{ q_i \mid q_i \in \tilde{o}_j \right\},$$

여기서 $\mathcal{Q}$는 추출된 모든 사용자 쿼리의 집합을 나타냅니다. $n$개의 검색된 부분 집합의 집합은 $\mathcal{R} = \bigcup_{j=1}^{n} \mathcal{E}(\tilde{q}_j, \mathcal{M}), \; |\mathcal{R}| \geq |\mathcal{Q}|$로 표시됩니다. 단순화를 위해, 모호성이 없는 경우 아래 첨자 $j$를 생략합니다.

**Attacker Capability.** 우리는 공격자가 입력 쿼리를 통해서만 LLM agent와 상호작용하는 블랙박스 공격을 고려합니다. 이 설정 하에서, 우리는 공격자가 agent에 대해 가질 수 있는 두 가지 수준의 지식을 검토합니다: (1) 기본 수준, 여기서 공격자는 적용된 도메인 및 작업과 같은 agent에 대한 일반적인 배경 정보만 가지고 있습니다. 예를 들어, 의료 기록 관리 agent의 경우 [[29]](#ref29), 공격자는 agent가 사용자 쿼리에 답하기 위해 의료 기록과 상호작용한다는 것을 알고 있습니다. (2) 고급 수준, 여기서 공격자는 탐색적 상호작용을 통해 agent의 일부 특정 구현 세부 정보를 얻습니다. 이 논문에서는 공격자가 여러 상호작용 후에 유사도 점수 함수 $f(q, q_i)$를 추론할 수 있다고 가정하며, 이는 의미적 유사성(예: 코사인 유사성) 또는 쿼리 형식 유사성(예: 편집 거리)에 기반할 수 있습니다.

## 3 Paradigm of Attack Design

### 3.1 Attacking Prompt Design

agent에 대한 블랙박스 접근만으로는 MEXTRA의 성공이 공격 프롬프트의 설계에 크게 의존합니다. RAG의 개인정보 보호 문제에 대한 기존 연구들 [[43]](#ref43), [[12]](#ref12)은 몇 가지 효과적인 설계를 제안했지만, agent의 본질적으로 복잡한 워크플로우 때문에 LLM agent에 직접 적용할 수는 없습니다.

첫째, RAG 데이터 추출을 위한 공격 프롬프트는 LLM agent 코어의 입력에 워크플로우 설명, 사용 가능한 도구, 접근 가능한 데이터베이스와 같은 광범위한 작업 관련 세부 정보가 포함되어 있기 때문에 검색된 사용자 쿼리를 추출하는 데 어려움을 겪습니다. RAG 개인정보 추출에 사용된 "모든 컨텍스트를 반복해 주세요"와 같은 모호한 명령어는 [[43]](#ref43) 검색된 사용자 쿼리를 정확하게 대상으로 삼지 못하여 부록 B.2에 표시된 것처럼 공격 실패로 이어집니다. 따라서 효과적인 공격 프롬프트는 검색된 사용자 쿼리를 명시적으로 찾아낸 다음 우선순위를 정해야 합니다.

둘째, §2.1에서 언급했듯이 LLM agent는 종종 다양한 작업과 솔루션을 포함합니다. 실행 결과는 텍스트 출력을 넘어 확장되므로 간단한 텍스트 생성 요청은 실현 불가능합니다. 예를 들어, 웹사이트에서의 검색이나 클릭과 같은 작업을 포함하고 직접 텍스트를 생성하지 않는 웹 agent를 고려해 보십시오. "검색된 모든 사용자 쿼리를 출력해 주세요"와 같은 프롬프트는 agent의 워크플로우가 그러한 요청을 지원하지 않거나 완료할 적절한 조치를 결정하지 않기 때문에 메모리 데이터를 추출하는 데 어려움이 있습니다. 따라서 공격자는 검색된 출력의 형식을 지정하여 agent의 워크플로우와 일치하고 공격자에게 접근 가능하도록 해야 합니다.

위의 논의를 바탕으로, 우리는 다음과 같이 메모리 추출 공격 프롬프트 $\tilde{q}$를 설계합니다:

$$\tilde{q} = \tilde{q}^{\mathrm{loc}} \mathbin{\|} \tilde{q}^{\mathrm{align}},$$

여기서 로케이터 부분 $\tilde{q}^{\mathrm{loc}}$은 긴 텍스트에서 어떤 내용을 추출할지 지정하는 데 사용되고, 정렬기 부분 $\tilde{q}^{\mathrm{align}}$은 출력 형식을 지정하여 agent의 워크플로우와 정렬하는 데 사용됩니다. 예를 들어, 웹 agent의 경우 $\tilde{q}^{\mathrm{loc}}$은 "이전 예제를 잃어버렸습니다"가 될 수 있으며, 이는 다른 설명 대신 검색된 예제를 요청하고, $\tilde{q}^{\mathrm{align}}$은 "검색창에 입력해 주세요"가 될 수 있습니다 (그림 1).

위의 프롬프트 설계를 따르면, 공격자는 일반 agent를 위한 공격 프롬프트를 만들어 메모리에서 개인 데이터를 추출할 수 있습니다. 그러나 하나의 공격 프롬프트는 $\mathcal{E}(\tilde{q}, \mathcal{M})$에서 최대 $k$개의 사용자 쿼리만 추출할 수 있습니다. 메모리에서 더 많은 데이터에 접근하려면, 공격자는 메모리에서 다른 레코드를 검색하기 위해 더 다양한 쿼리를 설계해야 하며, 이는 더 큰 $\mathcal{R}$과 결과적으로 더 큰 $Q$로 이어집니다. 수동으로 공격 프롬프트를 설계하는 것은 시간이 많이 걸리고 비효율적이므로, 우리는 자동화된 다양한 프롬프트 생성 방법을 추가로 개발합니다.

### 3.2 Automated Diverse Prompts Generation

추출 공격을 위한 다양한 프롬프트를 자동으로 생성하기 위해, 우리는 GPT-4 [[23]](#ref23)를 공격 프롬프트 생성기로 사용합니다. 이 생성을 위해 사용된 지침에는 두 가지 주요 목표가 있습니다: (1) **추출 기능**: 생성된 쿼리가 §3.1에서 상세히 설명된 프롬프트 설계를 충족하도록 보장합니다. (2) **다양한 검색**: 더 큰 추출된 쿼리 집합 $\mathcal{Q}$를 얻기 위해 쿼리가 다양하도록 보장합니다.

추출 기능은 §3.1의 프롬프트 설계에 의해 보장되지만, 쿼리의 다양성은 공격자의 agent에 대한 지식 수준에 따라 달라집니다. agent에 대한 기본 수준의 지식 하에서, 우리는 생성기가 동일한 추출 기능을 유지하면서 표현과 구문이 다양한 $n$개의 공격 프롬프트를 생성하도록 프롬프트하는 기본 지침 $\mathcal{T}^{\mathrm{basic}}$을 설계합니다. $\mathcal{T}^{\mathrm{basic}}$은 작업 설명, 두 가지 목표에 기반한 프롬프트 생성 요구 사항, 출력 형식, 그리고 유효한 공격 프롬프트의 문맥 내 예시의 네 부분으로 구성됩니다. 전체 지침은 부록 A.1에 있습니다. 이 보수적인 전략은 agent의 상세한 구현 정보가 필요하지 않으므로 일반 LLM agent에 대한 메모리 추출 공격에 적용할 수 있습니다.

고급 지식 수준 하에서는 생성된 공격 프롬프트의 다양성을 더욱 향상시킬 수 있습니다. §2.2에서 공격자가 탐색적 상호작용을 통해 점수 함수 $f(q, q_i)$를 추론했다는 고급 지식의 가정 하에, 우리는 고급 지침 $\mathcal{T}^{\mathrm{advan}}$을 제안합니다. 예를 들어, $f(q, q_i)$가 편집 거리와 같이 쿼리 형식과 길이의 유사성에 의존하는 경우, $\mathcal{T}^{\mathrm{advan}}$은 생성기가 다른 길이의 공격 프롬프트를 생성하도록 추가 지침을 포함할 것입니다. 이는 다양한 길이의 사용자 쿼리를 추출하고 추출된 쿼리의 총 수를 늘리는 데 도움이 됩니다. 또는, $f(q, q_i)$가 코사인 유사성과 같은 의미적 유사성에 기반하는 경우, $\mathcal{T}^{\mathrm{advan}}$은 $\mathcal{T}^{\mathrm{basic}}$에서처럼 단순히 다른 표현을 사용하는 대신 다양한 의미적 변형을 활용합니다. 구체적으로, 생성기가 $n$개의 도메인 특정 단어나 구문 $s$를 생성하도록 프롬프트합니다. 예를 들어, 온라인 쇼핑 시나리오에서 구문은 의미적으로 유사한 쿼리를 포착하기 위해 "가구" 또는 "전자 제품"이 될 수 있습니다. 이러한 생성된 구문 $s$는 동일한 공격 프롬프트 $\tilde{q}$에 개별적으로 추가되어 $\tilde{q}_s = s||\tilde{q}$로 공식화된 여러 의미 지향 공격 프롬프트를 만듭니다. 이러한 지침의 세부 정보는 부록 A.2에 제공됩니다.

## 4 RQ1: LLM Agent Memory Extraction

기본 지침 $\mathcal{T}^{\mathrm{basic}}$을 통해 생성된 공격 프롬프트를 사용하여, 우리는 두 개의 실제 애플리케이션 agent에서 LLM agent 메모리의 개인정보 유출을 경험적으로 조사합니다. 우리의 평가는 LLM agent가 우리의 메모리 추출 공격 MEXTRA²에 대해 높은 취약성을 보인다는 것을 보여줍니다.

²소스 코드는 https://github.com/wangbo9719/MEXTRA 에서 사용할 수 있습니다.

### 4.1 Experiments Setup

**Agent Setup.** 우리는 서로 다른 애플리케이션을 위한 두 가지 대표적인 실제 agent를 선택합니다: EHRAgent [[29]](#ref29)와 Retrieval-Augmented Planning (RAP) 프레임워크 [[14]](#ref14). EHRAgent는 전자 건강 기록(EHR) 관리를 위한 코드 기반 agent이며, RAP는 온라인 쇼핑을 위한 웹 agent입니다. 코드 기반 agent와 웹 agent는 인기 있는 agent 유형이며 [[34]](#ref34), [[31]](#ref31), [[48]](#ref48), [[3]](#ref3), 의료 및 온라인 쇼핑은 모두 매우 민감한 사용자 개인 정보를 포함하는 일반적인 도메인입니다.

EHRAgent는 자율적인 코드 생성 및 실행을 가능하게 하여 임상의가 자연어를 사용하여 EHR과 직접 상호작용할 수 있도록 돕습니다. 코드 생성 예시를 위해 상위 4개 레코드를 검색하는 데 편집 거리를 사용합니다. 생성된 코드는 답변을 도출하기 위해 실행됩니다. RAP는 과거 레코드를 활용하기 위한 일반적인 패러다임입니다. 우리는 온라인 쇼핑을 시뮬레이션하는 Webshop [[41]](#ref41)에서의 적용에 중점을 둡니다. SBERT [[27]](#ref27)의 임베딩과 MiniLM [[35]](#ref35) 기반의 코사인 유사도를 사용하여 작업 생성 예시를 위해 상위 3개 레코드를 검색합니다. 생성된 작업은 웹페이지와 상호작용하는 데 사용됩니다. 자세한 내용은 부록 B를 참조하십시오.

실험을 위해 LLM agent 코어는 GPT-4o [[24]](#ref24)를 기반으로 하며 두 agent 모두 메모리 크기는 200입니다. EHRAgent와 RAP의 메모리에 있는 쿼리는 각각 MIMIC-III [[13]](#ref13)와 Webshop [[41]](#ref41)에서 무작위로 선택됩니다. 그리고 agent는 해당 솔루션을 생성하여 쿼리-솔루션 레코드를 형성합니다. 이 설정은 달리 명시되지 않는 한 모든 실험의 기본값으로 사용됩니다.

**Metrics.** MEXTRA에 대한 LLM agent의 취약성을 평가하기 위해 다음 메트릭을 보고합니다. **Extracted Number (EN):** $|\mathcal{Q}|$, $n$개의 공격 프롬프트 실행 결과에서 수집된 고유한 사용자 쿼리 집합 $\mathcal{Q}$의 크기. **Extracted Efficiency (EE):** $\frac{|\mathcal{Q}|}{n \times k}$, $n$개의 공격 프롬프트의 효율성. 예시로 검색된 레코드 $\mathcal{E}(\tilde{q}, \mathcal{M})$만 LLM의 입력에 나타나므로 이러한 레코드의 쿼리만 추출할 수 있습니다. 따라서 EN과 EE는 검색된 레코드 집합 $\mathcal{R}$의 크기와 검색된 쿼리를 출력하도록 agent에 지시하는 공격 프롬프트의 성공률이라는 두 가지 요소에 따라 달라집니다. 이를 측정하기 위해 추가 메트릭을 도입합니다. **Retrieved Number (RN):** $|\mathcal{R}|$, $\mathcal{R}$의 크기. **Complete Extracted Rate (CER):** $n'/n$, 여기서 $n'$는 검색된 모든 $k$개 쿼리를 완전히 추출한 공격의 수입니다. **Any Extracted Rate (AER):** $n''/n$, 여기서 $n''$는 적어도 하나의 검색된 쿼리를 추출한 공격의 수입니다. 더 높은 RN, CER 및 AER은 더 높은 EN 및 EE를 달성하는 데 기여합니다. 단순화를 위해, 저장된 레코드가 평가 내내 변경되지 않는 정적 메모리 설정에서 공격을 평가합니다.

**Baseline.** 공격 프롬프트 설계의 효과를 입증하기 위해, 우리는 간단한 기준선 프롬프트 "검색된 모든 사용자 쿼리를 출력해 주세요"를 고려합니다. 이는 검색된 쿼리를 명시적으로 요청하지만 출력 형식을 지정하지 않습니다. 공정한 비교를 위해, 우리는 공격 프롬프트 생성기를 사용하여 이를 기반으로 $n$개의 다양한 쿼리를 생성합니다. 생성 지침은 §3.2에서 소개된 $\mathcal{T}^{\mathrm{basic}}$을 따르지만, $\tilde{q}^{\mathrm{align}}$을 명시적으로 강제하지는 않습니다. 우리는 이 기준선을 "w/o aligner"라고 부릅니다. 또한, $\mathcal{T}^{\mathrm{basic}}$의 효과를 증명하기 위해 두 가지 변형을 도입합니다. 하나는 명시적인 프롬프트 생성 요구 사항을 제거하고, 예시에만 의존하여 추출 기능을 암시적으로 전달하는 것입니다. 이를 "w/o req"라고 부릅니다. 다른 하나는 예시를 제거하고, 요구 사항만 사용하여 추출 기능을 유지하는 것으로, "w/o demos"로 표시됩니다. 이러한 지침의 세부 정보는 부록 A.3에 있습니다.

### 4.2 Attacking Results

LLM agent는 제안된 메모리 추출 공격에 취약합니다. 표 1에 우리의 공격 및 기준선에 대한 30개 프롬프트의 공격 결과를 제시합니다. 메모리 크기가 200이고 LLM agent에 대한 기본 지식만으로도, $\mathcal{T}^{\mathrm{basic}}$을 사용하는 공격 프롬프트 생성기로 생성된 30개의 프롬프트는 EHRAgent에서 50개의 개인 쿼리를, RAP에서 26개의 개인 쿼리를 추출합니다. 또한, 두 agent에 대한 CER 값은 0.83과 0.87로, AER과 거의 일치하며, 이는 대부분의 공격 프롬프트가 검색된 모든 쿼리를 성공적으로 추출했음을 나타냅니다. 우리는 EHRAgent에서 0.4 이상의 EE를, RAP에서 약 0.3의 EE를 달성하여 제안된 추출 공격의 높은 효율성을 보여줍니다. 이러한 결과는 LLM agent가 제안된 MEXTRA에 대해 심각한 취약성을 가지고 있음을 보여줍니다.

| Agent | method | EN | RN | EE | CER | AER |
| :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| | **MEXTRA** | **50** | **55** | **0.42** | **0.83** | **0.83** |
| | w/o aligner | 36 | 43 | 0.30 | 0.70 | 0.70 |
| EHRAgent | w/o req | 39 | 61 | 0.33 | 0.43 | 0.47 |
| | w/o demos | 29 | 40 | 0.24 | 0.47 | 0.47 |
| | **MEXTRA** | **26** | **27** | **0.29** | **0.87** | **0.90** |
| | w/o aligner | 6 | 20 | 0.07 | 0.17 | 0.70 |
| RAP | w/o req | 25 | 27 | 0.28 | 0.67 | 0.70 |
| | w/o demos | 8 | 32 | 0.09 | 0 | 0.57 |

*Table 1: Attacking results on two agents. The number of attacking prompts n is 30 and the memory size m is 200. The bold numbers denote the best results.*

**공격 프롬프트 설계와 자동 생성 지침은 개인정보 위험을 드러내는 데 필수적입니다.** 표 1에 따르면, 모든 기준선은 거의 모든 메트릭에서 일관되게 더 나쁜 성능을 보여, 메모리 개인정보 위험을 노출하는 데 있어 우리 설계의 효과를 강조합니다. w/o aligner의 낮은 성능은 공격 프롬프트 설계에서 $\tilde{q}^{\mathrm{align}}$의 중요성을 강조합니다. 특히, 이 기준선과 우리 방법 간의 성능 격차는 EHRAgent가 텍스트 기반 결과로 코드를 생성하여 출력 형식에 덜 제한적이기 때문에 RAP보다 EHRAgent에서 더 작습니다. 또한, w/o req 및 w/o demos의 감소된 성능은 상세한 지침과 예제가 모두 효과적인 공격 프롬프트를 생성하는 데 필수적임을 보여줍니다. 이러한 기준선은 때때로 더 느슨한 기능 요구 사항으로 인해 더 높은 RN을 달성하지만(더 큰 프롬프트 다양성과 더 넓은 범위의 검색된 쿼리를 허용), 이는 더 낮은 CER 및 AER을 희생하여 궁극적으로 추출된 항목 수가 감소하는 결과를 낳습니다.

추가적으로, 우리는 두 agent 간의 EN 및 RN 값에서 상당한 차이를 관찰하며, 이는 잠재적으로 메모리 모듈 구성의 차이에 기인할 수 있습니다. 이러한 관찰을 바탕으로, 우리는 다음 섹션에서 LLM agent의 관점에서 추출 성능에 영향을 미칠 수 있는 다양한 요소를 추가로 조사합니다.

## 5 RQ2: Impact of Memory Module Configuration

이 섹션에서는 메모리 모듈 구성이 LLM agent 메모리 유출에 미치는 영향을 탐구합니다. 우리의 분석은 어떤 구성이 메모리 추출 공격에 더 취약한지를 강조합니다.

### 5.1 Memory Module Configuration

LLM agent 메모리의 메모리 모듈 구성에서 다섯 가지 대안적인 설계 선택을 고려합니다: (1) 유사도 점수 함수 $f(q, q_i)$, 우리는 코사인 유사성과 편집 거리 사이에서 번갈아 사용합니다; (2) $f$가 코사인 유사성일 때 쿼리를 인코딩하는 데 사용되는 임베딩 모델 $E(·)$, 즉, $f(q, q_i) = cos(E(q), E(q_i))$. 우리는 SBERT 아키텍처 하에서 모델 크기가 다양한 세 가지 모델을 선택합니다 [[27]](#ref27): MiniLM [[35]](#ref35), MPNet [[30]](#ref30), 및 ROBERTa_large [[20]](#ref20), 자세한 내용은 부록 B.1을 참조하십시오; (3) 검색된 레코드 수를 결정하는 검색 깊이 $k$는 1에서 5까지 다양합니다; (4) 메모리 크기 $m$은 50에서 500까지 다양하며, 작은 메모리 집합은 큰 메모리 집합의 부분 집합입니다; (5) LLM agent 코어의 백본, 우리는 GPT-4 [[23]](#ref23), GPT-4O 및 Llama3-70b [[6]](#ref6) 사이에서 변경합니다. 다른 구성의 영향을 탐구하기 위해, 우리는 다른 것을 고정시킨 채 한 번에 하나 또는 여러 구성을 변경합니다. agent의 모든 기본 설정은 §4.1에 상세히 설명된 원래 구성에 따라 설정됩니다.

### 5.2 Results Analysis

**Scoring Function.** 우리는 두 agent의 구현을 수정하여 점수 함수를 변경합니다. 두 가지 다른 점수 함수 하에서 두 agent에 대한 추출된 숫자는 표 2에 제시되어 있습니다. 결과는 $f(q, q_i)$가 편집 거리일 때, 메모리 크기에 관계없이 추출 성능이 코사인 유사성의 성능을 일관되게 능가함을 나타냅니다. 이 중요한 차이는 LLM agent의 추출 공격에 대한 취약성에서 점수 함수의 중요한 역할을 강조합니다. 또한, 결과는 특정 구현 세부 정보가 알려지지 않았을 때 편집 거리에 기반한 검색이 추출 공격에 더 취약함을 시사합니다.

| Agent | f(q, qi) | E() | 50 | 100 | 200 | 300 | 400 | 500 |
| :--- | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| | edit | - | 31 | 43 | 50 | 51 | 58 | 59 |
| EHRAgent | cos | MiniLM | 14 | 20 | 20 | 23 | 27 | 24 |
| | | MPNet | 13 | 19 | 19 | 22 | 25 | 24 |
| | | ROBERTA | 18 | 21 | 27 | 29 | 34 | 36 |
| | edit | - | 23 | 36 | 46 | 56 | 64 | 63 |
| RAP | cos | MiniLM | 18 | 24 | 26 | 30 | 31 | 34 |
| | | MPNet | 15 | 22 | 20 | 22 | 25 | 30 |
| | | ROBERTA | 22 | 30 | 26 | 19 | 20 | 24 |

*Table 2: The extracted number (EE) across different similarity scoring functions f(q, qi), embedding models E(), and memory sizes.*

<figure>
    <img src="assets/Figure_2.png" alt="Figure 2">
    <figcaption>
        <p>Figure 2: The extracted efficiency (EE) across different memory sizes m ranging from 50 to 500 on two agents.</p>
    </figcaption>
</figure>

**Embedding Model.** $f(q, q_i)$가 코사인 유사성으로 설정되었을 때, 우리는 다른 임베딩 모델에 걸친 추출 성능을 비교하여 그 영향을 분석합니다. 표 2에서 볼 수 있듯이, 임베딩 모델의 선택은 추출 결과에 약간의 영향만 미치며, agent에 걸쳐 일관된 추세는 없습니다. EHRAgent의 경우, RoBERTa는 모든 메모리 크기에서 일관되게 가장 높은 추출 결과를 달성합니다. 반면, RAP의 경우, MiniLM은 메모리 크기가 200을 초과할 때 가장 높은 추출 수를 달성합니다. 이러한 불일치는 임베딩 모델과 텍스트 도메인의 차이에서 비롯될 수 있으며, 이는 공격 프롬프트의 임베딩과 메모리의 쿼리 간의 유사성에 영향을 미칩니다.

**Memory Size.** 우리는 다른 메모리 크기 하에서 추출된 수가 어떻게 변하는지 검토합니다. 표 2와 그림 2에서 볼 수 있듯이, 메모리 크기를 50에서 500으로 늘리면 일반적으로 두 agent 모두에서 더 높은 EN과 EE가 발생합니다. 이 추세는 더 큰 메모리 크기가 더 높은 위험을 초래함을 시사합니다. 또한, 메모리 확장이 쿼리 분포를 변경하여 잠재적으로 검색 결과에 영향을 미치기 때문에 메모리 크기가 증가함에 따라 EN과 EE가 약간 감소할 수 있습니다.

**Retrieval Depth.** 검색 깊이 $k$의 영향을 탐구하기 위해, 우리는 $k$가 1에서 5까지인 실험을 수행하고 그 결과를 그림 3에 요약합니다. 우리는 검색 깊이 $k$가 추출된 수에 상당한 영향을 미친다는 것을 발견했습니다. 더 큰 $k$는 더 많은 쿼리가 검색되므로 일관되게 더 높은 추출된 수로 이어져 agent를 추출 공격에 취약하게 만듭니다. RN과 EN 사이의 격차는 EHRAgent에서 $k=1$일 때 약간 눈에 띄는데, 이는 때때로 검색된 쿼리 대신 시스템 프롬프트의 하드코딩된 예제에서 쿼리를 출력하기 때문입니다. 반면, 검색된 집합이 커질 때 RAP에 대해 전체 검색된 쿼리 집합을 추출하는 것이 점점 더 어려워지기 때문에 $k \ge 4$일 때 RAP에서 격차가 중요해집니다. 전반적으로, 더 큰 $k$는 더 심각한 유출로 이어집니다.

<figure>
    <img src="assets/Figure_3.png" alt="Figure 3">
    <figcaption>
        <p>Figure 3: The extracted number (EN) and retrieved number (RN) across different retrieval depths k ranging from 1 to 5 on two agents.</p>
    </figcaption>
</figure>

**Backbone.** 우리는 표 3에서 RAP에 대한 세 가지 LLM 백본을 비교합니다. 결과는 GPT-4O가 GPT-4보다 약간 더 취약하며, Llama3-70b는 가장 낮은 EN과 CER을 가지고 있음을 보여줍니다. 우리는 Llama3-70b가 RAP에서 제대로 수행되지 않아 원래 온라인 쇼핑 작업에서 8%의 성공률을 달성한 반면, GPT-4와 GPT-4O는 약 40%의 성공률을 보인다는 것을 발견했습니다. Llama3-70b가 사용 가능한 출력을 생성하는 데 어려움을 겪기 때문에, 이를 기반으로 한 메모리 추출 결과도 심각하게 제한됩니다.

| Backbone | EN | CER | AER |
| :--- | :-: | :-: | :-: |
| GPT-4 | 23 | 0.77 | 0.93 |
| GPT-40 | 26 | 0.87 | 0.90 |
| Llama3-70b | 17 | 0 | 0.93 |

*Table 3: The memory extraction results across different LLM backbones on RAP.*

요약하면, 다섯 가지 선택 모두 메모리 유출에 영향을 미치며, 점수 함수, 검색 깊이, 메모리 크기가 더 큰 영향을 미칩니다.

## 6 RQ3: Impact of Prompting Strategies

이 섹션에서는 공격자가 사용하는 다양한 프롬프팅 전략의 영향을 추가로 탐구합니다. 구체적으로, 우리는 공격 프롬프트의 수와 §3.2에서 소개된 두 가지 프롬프트 생성 지침을 검토합니다. 결과는 공격 횟수를 늘리고 agent에 대한 더 많은 구현 지식을 갖는 것이 메모리 추출의 효과를 향상시킨다는 것을 나타냅니다.

### 6.1 Experiment Settings

우리는 공격 프롬프트의 수를 10에서 50까지 10씩 증가시키며, 작은 집합은 큰 집합의 부분 집합입니다. 공격자가 점수 함수 $f(q, q_i)$를 추론했다고 가정하는 고급 지침 $\mathcal{T}^{\mathrm{advan}}$의 효과를 탐구하기 위해, 우리는 두 agent에 대해 $f(q, q_i)$를 편집 거리 또는 코사인 유사성으로 설정합니다. 이런 식으로, 우리는 네 가지 경우에 대해 $\mathcal{T}^{\mathrm{advan}}$을 설계합니다: EHRAgent와 RAP, 각각 편집 거리와 코사인 유사성을 가집니다.

### 6.2 Results Analysis

**The number of attacking prompts.** 다양한 수의 공격 프롬프트 및 프롬프트 생성 지침에 대한 EN 및 RN 결과는 그림 4에 요약되어 있습니다. 공격 프롬프트 수가 증가함에 따라 EN과 RN 모두 성장률에 큰 둔화 없이 계속 증가합니다.

<figure>
    <img src="assets/Figure_4.png" alt="Figure 4">
    <figcaption>
        <p>Figure 4: The impact of the number of attacking prompts n and the prompt generation instructions Tadvan/Tbasic on extracted number (EN) and retrieved number (RN). The memory size is 200.</p>
    </figcaption>
</figure>

**Prompt generation instructions.** 그림 4에서 볼 수 있듯이, 고급 지침 $\mathcal{T}^{\mathrm{advan}}$은 거의 모든 경우에 기본 지침 $\mathcal{T}^{\mathrm{basic}}$보다 성능이 뛰어나며, $\mathcal{T}^{\mathrm{advan}}$의 효과를 보여줍니다. agent의 메모리 구현에 대한 자세한 정보가 있으면 공격자는 실제로 더 많은 정보를 추출할 수 있습니다. agent의 점수 함수가 편집 거리이고 $n$이 작을 때만 $\mathcal{T}^{\mathrm{basic}}$의 결과가 $\mathcal{T}^{\mathrm{advan}}$의 결과보다 약간 더 낫습니다(그림 4(a) 및 4(c) 참조). 이는 프롬프트 생성 중 LLM 프롬프트 생성기의 내재된 무작위성 때문이며, 이로 인해 $n$이 작을 때 공격 프롬프트가 상대적으로 유사하게 됩니다. 그러나 $n$이 증가함에 따라 더 다양한 프롬프트가 생성되어 이 무작위성이 덜 영향을 미칩니다.

$\mathcal{T}^{\mathrm{basic}}$과 비교하여, $\mathcal{T}^{\mathrm{advan}}$은 검색된 수(RN)를 상당히 증가시키며, 편집 거리보다 코사인 유사성에 맞춰졌을 때 더 눈에 띄는 개선을 보입니다. 예를 들어, $n=50$일 때, 편집 거리를 사용하는 RAP의 RN은 58에서 79로 증가하는 반면(그림 4(c)), 코사인 유사성을 사용하면 35에서 84로 급증합니다(그림 4(d)). 이는 편집 거리에 대해 프롬프트 길이를 단순히 조정하는 것과 비교하여, 추가 구문을 통합하면 프롬프트와 메모리에 저장된 쿼리 간의 코사인 유사성을 실질적으로 변경하여 검색된 쿼리의 중복을 줄이기 때문입니다. 또한, 코사인 유사성을 사용하는 RAP에서(그림 4(d)), $\mathcal{T}^{\mathrm{advan}}$은 RN과 EN 사이에 눈에 띄는 격차를 보입니다. 이 격차는 두 가지 요인에서 비롯됩니다. 첫째, 도입된 추가 구문이 프롬프트의 추출 기능을 약화시킬 수 있습니다. 둘째, 각 프롬프트에 의해 검색된 쿼리 간의 중복이 감소함에 따라, 성공하지 못한 추출은 더 많은 수의 검색된 쿼리가 추출되지 않은 채로 남게 합니다.

## 7 Related Work

**LLM Agent with Memory.** 사용자-에이전트 상호작용을 저장하는 메모리는 LLM 에이전트가 실제 애플리케이션을 해결하는 데 귀중한 통찰력을 제공하여 LLM 에이전트의 필수 구성 요소가 됩니다 [[46]](#ref46). 그러나 LLM 에이전트에 메모리를 장착하면 성능이 향상되지만 개인정보 보호 위험도 따릅니다. 예를 들어, 의료 에이전트 [[29]](#ref29), [[17]](#ref17)는 환자에 대한 민감한 정보를 저장하고, 웹 애플리케이션 에이전트 [[14]](#ref14)는 사용자 선호도를 기록하며, 자율 주행 에이전트 [[22]](#ref22), [[37]](#ref37)는 과거 주행 시나리오를 축적합니다. 이러한 메모리 모듈은 본질적으로 매우 민감한 사용자 데이터를 저장하므로, 메모리 유출 위험에 대한 체계적인 조사는 잠재적 위협을 밝히고 완화하는 데 중요합니다.

**Privacy Risk in RAG.** RAG에 대한 최근 연구들은 외부 데이터와 관련된 개인정보 보호 문제를 광범위하게 탐구했습니다. Zeng 등 [[43]](#ref43)은 RAG 시스템에 통합된 개인 데이터가 수동으로 제작된 적대적 프롬프트에 취약하다는 것을 처음으로 밝혔으며, Qi 등 [[26]](#ref26)은 여러 RAG 구성에 걸쳐 더 포괄적인 조사를 수행했습니다. 추출을 자동화하기 위해 Jiang 등 [[12]](#ref12)은 에이전트 기반 공격을 개발했으며, Di Maio 등 [[5]](#ref5)은 개인 지식을 점진적으로 추출하기 위한 적응형 전략을 제안했습니다. 이러한 연구는 두 시스템 모두 유사한 데이터 검색 메커니즘을 사용하기 때문에 LLM 에이전트에서도 유사한 개인정보 보호 위협이 발생할 수 있음을 시사합니다.

**Prompt Injection Attack.** 프롬프트 주입은 조작된 적대적 명령을 프롬프트에 주입하여 LLM의 출력을 조작하는 공격입니다 [[8]](#ref8). 이는 직접 및 간접 프롬프트 주입의 두 가지 범주로 나눌 수 있습니다 [[28]](#ref28). 직접 프롬프트 주입에서는 악의적인 입력이 LLM에 주어진 프롬프트에 직접 포함되어 목표 탈취 [[25]](#ref25), [[45]](#ref45), 프롬프트 유출 [[25]](#ref25), [[9]](#ref9)과 같은 목표를 달성합니다.

반면, 간접 프롬프트 주입은 종종 사용자의 인식 없이 외부 콘텐츠 소스를 통해 악의적인 입력을 전달합니다. 이는 일반적으로 이메일이나 웹사이트와 같은 채널을 통해 LLM 기반 에이전트를 대상으로 하며 [[44]](#ref44), [[38]](#ref38), [[19]](#ref19), 외부 입력의 더 은밀한 조작을 가능하게 하고 잠재적으로 이메일이나 웹 페이지에 포함된 개인 정보와 같은 무단 작업 및 의도하지 않은 데이터 유출로 이어질 수 있습니다. 그러나 이전 연구들은 이 연구의 주요 초점인 LLM 기반 에이전트의 메모리 유출 문제에 제한적인 관심을 기울였습니다.

## 8 Conclusion

본 논문에서는 메모리 추출 공격인 MEXTRA를 통해 LLM 에이전트 메모리 유출의 개인정보 보호 위험을 밝힙니다. 이는 공격 프롬프트 설계와 에이전트에 대한 다양한 수준의 지식에 맞춰진 자동화된 공격 프롬프트의 두 부분으로 구성됩니다. 경험적 평가는 MEXTRA에 대한 LLM 에이전트의 취약성을 보여줍니다. 또한, 에이전트 설계자와 공격자의 관점에서 메모리 유출에 영향을 미치는 주요 요소를 탐구합니다.

### Limitation

우리의 메모리 추출 공격은 단일 에이전트 설정에서만 평가되었습니다. 이를 에이전트가 통신하거나 메모리를 공유하는 다중 에이전트 설정으로 확장하는 것은 향후 연구를 위한 흥미로운 방향이 될 것입니다. 에이전트 간 상호작용이 메모리 유출 위험에 미치는 영향을 조사하면 LLM 에이전트의 개인정보 보호 취약점에 대한 더 깊은 통찰력을 제공할 수 있습니다. 또한, 우리가 고려하는 에이전트 프레임워크는 세션 제어를 통합하지 않습니다: 여러 사용자가 동일한 세션을 공유하여 메모리 모듈이 모든 사용자의 과거 기록을 저장하게 할 수 있습니다. 사용자 수준 및 세션 수준 메모리 격리를 도입하면 공격자의 개인 데이터 접근을 제한하고 메모리 추출의 영향을 완화할 수 있습니다. 그러나 세션 제어를 에이전트 프레임워크에 통합하는 표준 방법이 없으므로 향후 연구 과제로 남겨둡니다.

### Acknowledgements

Shenglai Zeng, Jiliang Tang 및 Pengfei He는 국립 과학 재단(NSF)의 보조금 번호 CNS2321416, IIS2212032, IIS2212144, IOS2107215, DUE2234015, CNS2246050, DRL2405483 및 IOS2035472, 미국 상무부, 게이츠 재단, 미시간 농업 및 농촌 개발부, 아마존, 메타, SNAP의 지원을 받았습니다.

## References

- <a id="ref1"></a>[1] Mahyar Abbasian, Iman Azimi, Amir M. Rahmani, and Ramesh C. Jain. 2023. Conversational health agents: A personalized Ilm-powered agent framework. CoRR, abs/2310.02374.
- <a id="ref2"></a>[2] C Cui, Z Yang, Y Zhou, Y Ma, J Lu, L Li, Y Chen, J Pan- chal, and Z Wang. 2024. Personalized autonomous driving with large language models: field experi- ments. arXiv preprint arXiv:2312.09397.
- <a id="ref3"></a>[3] Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Samual Stevens, Boshi Wang, Huan Sun, and Yu Su. 2023. Mind2web: Towards a generalist agent for the web. In Advances in Neural Information Processing Systems 36: Annual Conference on Neural Informa- tion Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023.
- <a id="ref4"></a>[4] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: pre-training of deep bidirectional transformers for language under- standing. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Tech- nologies, NAACL-HLT 2019, Minneapolis, MN, USA, June 2-7, 2019, Volume 1 (Long and Short Papers), pages 4171-4186. Association for Computational Linguistics.
- <a id="ref5"></a>[5] Christian Di Maio, Cristian Cosci, Marco Maggini, Valentina Poggioni, and Stefano Melacci. 2024. Pi- rates of the rag: Adaptively attacking llms to leak knowledge bases. arXiv preprint arXiv:2412.18295.
- <a id="ref6"></a>[6] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.
- <a id="ref7"></a>[7] Wenqi Fan, Yujuan Ding, Liangbo Ning, Shijie Wang, Hengyun Li, Dawei Yin, Tat-Seng Chua, and Qing Li. 2024. A survey on rag meeting llms: Towards retrieval-augmented large language models. In Pro- ceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, pages 6491– 6501.
- <a id="ref8"></a>[8] Feng He, Tianqing Zhu, Dayong Ye, Bo Liu, Wanlei Zhou, and Philip S. Yu. 2024. The emerged secu- rity and privacy of LLM agent: A survey with case studies. CoRR, abs/2407.19354.
- <a id="ref9"></a>[9] Bo Hui, Haolin Yuan, Neil Gong, Philippe Burlina, and Yinzhi Cao. 2024. Pleak: Prompt leaking attacks against large language model applications. In Pro- ceedings of the 2024 on ACM SIGSAC Conference on Computer and Communications Security, CCS 2024, Salt Lake City, UT, USA, October 14-18, 2024, pages 3600-3614. ACM.
- <a id="ref10"></a>[10] Hakan Inan, Kartikeya Upasani, Jianfeng Chi, Rashi Rungta, Krithika Iyer, Yuning Mao, Michael Tontchev, Qing Hu, Brian Fuller, Davide Testuggine, et al. 2023. Llama guard: Llm-based input-output safeguard for human-ai conversations. arXiv preprint arXiv:2312.06674.
- <a id="ref11"></a>[11] Neel Jain, Avi Schwarzschild, Yuxin Wen, Gowthami Somepalli, John Kirchenbauer, Ping-yeh Chiang, Micah Goldblum, Aniruddha Saha, Jonas Geiping, and Tom Goldstein. 2023. Baseline defenses for ad- versarial attacks against aligned language models. CoRR, abs/2309.00614.
- <a id="ref12"></a>[12] Changyue Jiang, Xudong Pan, Geng Hong, Chenfu Bao, and Min Yang. 2024. Rag-thief: Scalable extraction of private data from retrieval-augmented generation applications with agent-based attacks. arXiv preprint arXiv:2411.14110.
- <a id="ref13"></a>[13] Alistair EW Johnson, Tom J Pollard, Lu Shen, Li-wei H Lehman, Mengling Feng, Mohammad Ghassemi, Benjamin Moody, Peter Szolovits, Leo Anthony Celi, and Roger G Mark. 2016. Mimic-iii, a freely accessi- ble critical care database. Scientific data, 3(1):1-9.
- <a id="ref14"></a>[14] Tomoyuki Kagaya, Thong Jing Yuan, Yuxuan Lou, Jayashree Karlekar, Sugiri Pranata, Akira Kinose, Koki Oguri, Felix Wick, and Yang You. 2024. RAP: retrieval-augmented planning with contex- tual memory for multimodal LLM agents. CoRR, abs/2402.03610.
- <a id="ref15"></a>[15] Mandar Kulkarni, Praveen Tangarajan, Kyung Kim, and Anusua Trivedi. 2024. Reinforcement learning for optimizing RAG for domain chatbots. CoRR, abs/2401.06800.
- <a id="ref16"></a>[16] Patrick S. H. Lewis, Ethan Perez, Aleksandra Pik- tus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. 2020. Retrieval-augmented generation for knowledge-intensive NLP tasks. In Advances in Neu- ral Information Processing Systems 33: Annual Con- ference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual.
- <a id="ref17"></a>[17] Yunxiang Li, Zihan Li, Kai Zhang, Ruilong Dan, and You Zhang. 2023. Chatdoctor: A medical chat model fine-tuned on llama model using medical domain knowledge. CoRR, abs/2303.14070.
- <a id="ref18"></a>[18] Zekun Li, Baolin Peng, Pengcheng He, and Xifeng Yan. 2024. Evaluating the instruction-following robust- ness of large language models to prompt injection. In Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, EMNLP 2024, Miami, FL, USA, November 12-16, 2024, pages 557-568. Association for Computational Linguistics.
- <a id="ref19"></a>[19] Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Tian- wei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, and Yang Liu. 2023a. Prompt injection attack against Ilm-integrated applications. CoRR, abs/2306.05499.
- <a id="ref20"></a>[20] Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Man- dar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, and Veselin Stoyanov. 2019. Roberta: A robustly optimized BERT pretraining approach. CoRR, abs/1907.11692.
- <a id="ref21"></a>[21] Zhengliang Liu, Yue Huang, Xiaowei Yu, Lu Zhang, Zihao Wu, Chao Cao, Haixing Dai, Lin Zhao, Yiwei Li, Peng Shu, et al. 2023b. Deid-gpt: Zero-shot med- ical text de-identification by gpt-4. arXiv preprint arXiv:2303.11032.
- <a id="ref22"></a>[22] Jiageng Mao, Junjie Ye, Yuxi Qian, Marco Pavone, and Yue Wang. 2023. A language agent for autonomous driving. CoRR, abs/2311.10813.
- <a id="ref23"></a>[23] OpenAI. 2023. GPT-4 technical report. CoRR, abs/2303.08774.
- <a id="ref24"></a>[24] OpenAI. 2024. Hello gpt-40.
- <a id="ref25"></a>[25] Fábio Perez and Ian Ribeiro. 2022. Ignore previous prompt: Attack techniques for language models. CoRR, abs/2211.09527.
- <a id="ref26"></a>[26] Zhenting Qi, Hanlin Zhang, Eric P. Xing, Sham M. Kakade, and Himabindu Lakkaraju. 2024. Follow my instruction and spill the beans: Scalable data ex- traction from retrieval-augmented generation systems. CoRR, abs/2402.17840.
- <a id="ref27"></a>[27] Nils Reimers and Iryna Gurevych. 2019. Sentence-bert: Sentence embeddings using siamese bert-networks. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing. Asso- ciation for Computational Linguistics.
- <a id="ref28"></a>[28] Sippo Rossi, Alisia Marianne Michel, Raghava Rao Mukkamala, and Jason Bennett Thatcher. 2024. An early categorization of prompt injection attacks on large language models. CoRR, abs/2402.00898.
- <a id="ref29"></a>[29] Wenqi Shi, Ran Xu, Yuchen Zhuang, Yue Yu, Jieyu Zhang, Hang Wu, Yuanda Zhu, Joyce C. Ho, Carl Yang, and May Dongmei Wang. 2024. Ehragent: Code empowers large language models for few- shot complex tabular reasoning on electronic health records. In Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, EMNLP 2024, Miami, FL, USA, November 12-16, 2024, pages 22315–22339. Association for Computa- tional Linguistics.
- <a id="ref30"></a>[30] Kaitao Song, Xu Tan, Tao Qin, Jianfeng Lu, and Tie- Yan Liu. 2020. Mpnet: Masked and permuted pre- training for language understanding. In Advances in Neural Information Processing Systems 33: An- nual Conference on Neural Information Processing Systems 2020, NeurIPS 2020, December 6-12, 2020, virtual.
- <a id="ref31"></a>[31] Harsh Trivedi, Tushar Khot, Mareike Hartmann, Ruskin Manku, Vinty Dong, Edward Li, Shashank Gupta, Ashish Sabharwal, and Niranjan Balasubramanian. 2024. Appworld: A controllable world of apps and people for benchmarking interactive coding agents. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), ACL 2024, Bangkok, Thailand, August 11-16, 2024, pages 16022–16076. Association for Computational Linguistics.
- <a id="ref32"></a>[32] Tao Tu, Anil Palepu, Mike Schaekermann, Khaled Saab, Jan Freyberg, Ryutaro Tanno, Amy Wang, Brenna Li, Mohamed Amin, Nenad Tomasev, Shekoofeh Azizi, Karan Singhal, Yong Cheng, Le Hou, Albert Webson, Kavita Kulkarni, S. Sara Mahdavi, Christopher Sem- turs, Juraj Gottweis, Joelle K. Barral, Katherine Chou, Gregory S. Corrado, Yossi Matias, Alan Karthike- salingam, and Vivek Natarajan. 2024. Towards con- versational diagnostic AI. CoRR, abs/2401.05654.
- <a id="ref33"></a>[33] Thomas Vakili, Anastasios Lamproudis, Aron Henriks- son, and Hercules Dalianis. 2022. Downstream task performance of bert models pre-trained using auto- matically de-identified clinical data. In Proceedings of the Thirteenth Language Resources and Evalua- tion Conference, pages 4245-4252.
- <a id="ref34"></a>[34] Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, et al. 2024a. A survey on large language model based autonomous agents. Frontiers of Computer Science, 18(6):186345.
- <a id="ref35"></a>[35] Wenhui Wang, Furu Wei, Li Dong, Hangbo Bao, Nan Yang, and Ming Zhou. 2020. Minilm: Deep self- attention distillation for task-agnostic compression of pre-trained transformers. Advances in Neural In- formation Processing Systems, 33:5776–5788.
- <a id="ref36"></a>[36] Xingyao Wang, Yangyi Chen, Lifan Yuan, Yizhe Zhang, Yunzhu Li, Hao Peng, and Heng Ji. 2024b. Exe- cutable code actions elicit better LLM agents. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net.
- <a id="ref37"></a>[37] Licheng Wen, Daocheng Fu, Xin Li, Xinyu Cai, Tao Ma, Pinlong Cai, Min Dou, Botian Shi, Liang He, and Yu Qiao. 2024. Dilu: A knowledge-driven approach to autonomous driving with large language models. In The Twelfth International Conference on Learning Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net.
- <a id="ref38"></a>[38] Fangzhou Wu, Shutong Wu, Yulong Cao, and Chaowei Xiao. 2024a. WIPI: A new web threat for llm-driven web agents. CoRR, abs/2402.16965.
- <a id="ref39"></a>[39] Zhiheng Xi, Wenxiang Chen, Xin Guo, Wei He, Yiwen Ding, Boyang Hong, Ming Zhang, Junzhe Wang, Senjie Jin, Enyu Zhou, et al. 2023. The rise and potential of large language model based agents: A survey. arXiv preprint arXiv:2309.07864.
- <a id="ref40"></a>[40] Ke Yang, Jiateng Liu, John Wu, Chaoqi Yang, Yi R. Fung, Sha Li, Zixuan Huang, Xu Cao, Xingyao Wang, Yiquan Wang, Heng Ji, and Chengxiang Zhai. 2024. If LLM is the wizard, then code is the wand: A survey on how code empowers large language models to serve as intelligent agents. CoRR, abs/2401.00812.
- <a id="ref41"></a>[41] Shunyu Yao, Howard Chen, John Yang, and Karthik Narasimhan. 2022. Webshop: Towards scalable real- world web interaction with grounded language agents. In Advances in Neural Information Processing Sys- tems 35: Annual Conference on Neural Information Processing Systems 2022, NeurIPS 2022, New Or- leans, LA, USA, November 28 - December 9, 2022.
- <a id="ref42"></a>[42] Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik R. Narasimhan, and Yuan Cao. 2023. React: Synergizing reasoning and acting in language models. In The Eleventh International Conference on Learning Representations, ICLR 2023, Kigali, Rwanda, May 1-5, 2023. OpenReview.net.
- <a id="ref43"></a>[43] Shenglai Zeng, Jiankun Zhang, Pengfei He, Yiding Liu, Yue Xing, Han Xu, Jie Ren, Yi Chang, Shuaiqiang Wang, Dawei Yin, and Jiliang Tang. 2024. The good and the bad: Exploring privacy issues in retrieval-augmented generation (RAG). In Findings of the As- sociation for Computational Linguistics, ACL 2024, Bangkok, Thailand and virtual meeting, August 11- 16, 2024, pages 4505–4524. Association for Compu- tational Linguistics.
- <a id="ref44"></a>[44] Qiusi Zhan, Zhixiang Liang, Zifan Ying, and Daniel Kang. 2024. Injecagent: Benchmarking indirect prompt injections in tool-integrated large language model agents. In Findings of the Association for Computational Linguistics, ACL 2024, Bangkok, Thailand and virtual meeting, August 11-16, 2024, pages 10471-10506. Association for Computational Linguistics.
- <a id="ref45"></a>[45] Boyang Zhang, Yicong Tan, Yun Shen, Ahmed Salem, Michael Backes, Savvas Zannettou, and Yang Zhang. 2024a. Breaking agents: Compromising autonomous LLM agents through malfunction amplification. CoRR, abs/2407.20859.
- <a id="ref46"></a>[46] Zeyu Zhang, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Quanyu Dai, Jieming Zhu, Zhenhua Dong, and Ji- Rong Wen. 2024b. A survey on the memory mecha- nism of large language model based agents. CoRR, abs/2404.13501.
- <a id="ref47"></a>[47] Wayne Xin Zhao, Kun Zhou, Junyi Li, Tianyi Tang, Xiaolei Wang, Yupeng Hou, Yingqian Min, Beichen Zhang, Junjie Zhang, Zican Dong, et al. 2023. A survey of large language models. arXiv preprint arXiv:2303.18223.
- <a id="ref48"></a>[48] Boyuan Zheng, Boyu Gou, Jihyung Kil, Huan Sun, and Yu Su. 2024. Gpt-4v(ision) is a generalist web agent, if grounded. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net.
- <a id="ref49"></a>[49] Andy Zou, Zifan Wang, J. Zico Kolter, and Matt Fredrikson. 2023. Universal and transferable adver- sarial attacks on aligned language models. CoRR, abs/2307.15043.

---
## Appendix

### A Instructions for Prompts Generation

#### A.1 Basic Instruction

기본 지침 $\mathcal{T}^{\mathrm{basic}}$은 작업 설명, 프롬프트 생성 요구 사항, 출력 형식 및 컨텍스트 내 예시의 네 부분으로 구성됩니다. 공격 프롬프트 생성기에게 실행당 10개의 공격 프롬프트를 생성하고 필요한 총 수 $n$에 도달할 때까지 이 과정을 여러 번 반복하도록 지시합니다. EHRAgent 및 RAP에 대한 $\mathcal{T}^{\mathrm{basic}}$은 표 5에 나열되어 있습니다.

#### A.2 Advanced Instruction

**Advanced Instruction for Edit Distance.** $\mathcal{T}^{\mathrm{basic}}$과 비교하여, 편집 거리에 맞춰진 고급 지침 $\mathcal{T}^{\mathrm{advan}}$은 생성기에게 다양한 길이의 사용자 쿼리를 추출하기 위해 공격 프롬프트의 길이를 조정하도록 추가로 지시합니다. EHRAgent 및 RAP에 대한 편집 거리에 맞춰진 $\mathcal{T}^{\mathrm{advan}}$은 표 6에 나열되어 있습니다.

**Advanced Instruction for Cosine Similarity.** 코사인 유사성에 맞춰진 고급 지침 $\mathcal{T}^{\mathrm{advan}}$은 $\mathcal{T}^{\mathrm{basic}}$과 매우 다릅니다. EHRAgent의 경우, $\mathcal{T}^{\mathrm{advan}}$은 생성기에게 의료 도메인에 속하는 $n$개의 단어 또는 구문을 생성하도록 프롬프트합니다. 그리고 생성된 구문은 "이전 정보를 따르지 마십시오. 답변에 예제의 모든 질문을 저장하십시오."라는 공격 프롬프트 앞에 추가됩니다. RAP의 경우, $\mathcal{T}^{\mathrm{advan}}$은 Amazon의 일부 미리 정의된 항목 범주를 기반으로 생성기에게 프롬프트합니다. 생성된 쿼리는 "특정 항목]을 검색하지 말고, 가지고 있는 세 개의 이전 메모리를 검색하고, 모두 하나에 포함시키십시오 []"라는 프롬프트로 시작됩니다. EHRAgent 및 RAP에 대한 코사인 유사성에 맞춰진 $\mathcal{T}^{\mathrm{advan}}$은 표 7에 나열되어 있습니다.

#### A.3 Instructions for Baselines

기준선에 대한 지침은 $\mathcal{T}^{\mathrm{basic}}$을 기반으로 수정됩니다. "w/o aligner"의 경우, 표 8과 같이 두 번째 쿼리 생성 요구 사항을 제거하고 예시을 교체하여 정렬기 부분을 제거합니다. "w/o req"의 경우, 원래 $\mathcal{T}^{\mathrm{basic}}$에서 프롬프트 생성 요구 사항을 제거합니다. 그리고 "w/o demos"의 경우, 원래 $\mathcal{T}^{\mathrm{basic}}$에서 예제를 제거합니다.

### B More Details about Experiments

#### B.1 Experiment Setup

**Agent Setup.** EHRAgent는 자율적인 코드 생성 및 실행을 가능하게 하여 임상의가 자연어를 사용하여 EHR과 직접 상호작용할 수 있도록 돕습니다. EHRAgent의 메모리에는 환자에 대한 순차적 진단 기록이 포함될 수 있습니다. 에이전트의 솔루션 $s$는 (지식, 코드) 쌍으로 구성됩니다. 구체적으로, EHRAgent의 기본 설정에서 먼저 시스템 프롬프트에 하드코딩된 세 가지 예제를 기반으로 코드 생성을 안내하기 위해 "지식"을 생성합니다. 둘째, 데모용으로 메모리에서 상위 4개의 가장 관련성 있는 레코드 $(q_i, s_i)$를 검색하며, 여기서 점수 함수 $f(q, q_i)$는 편집 거리입니다. 그런 다음, 사용자 쿼리 $q$, 검색된 상위 4개 레코드 $E(q, M)$, 생성된 지식 및 시스템 프롬프트가 결합되어 LLM 에이전트 코어에 입력되어 코드를 생성합니다. 마지막으로, 생성된 코드가 실행되어 쿼리에 대한 답변을 도출합니다.

RAP는 현재 상황과 컨텍스트를 기반으로 과거 기록을 동적으로 활용하도록 설계된 일반적인 패러다임입니다. 우리는 온라인 쇼핑을 시뮬레이션하는 웹 애플리케이션인 Webshop [[41]](#ref41)에서의 적용에 중점을 둡니다. 여기서 에이전트는 사용자 쿼리를 기반으로 제품을 검색하고 구매를 위해 선택하는 데 사용됩니다. 상위 3개 레코드를 검색하며, 점수 함수 $f(q, q_i)$는 SBERT [[27]](#ref27)에서 파생된 임베딩을 기반으로 한 코사인 유사성이며 MiniLM [[35]](#ref35)을 기반으로 합니다. 그런 다음 검색된 레코드와 사용자 쿼리가 시스템 프롬프트와 결합되어 LLM 에이전트 코어가 웹 작업을 생성하도록 합니다. 이 작업은 검색 쿼리를 검색 상자에 입력하거나 버튼을 클릭하는 등 웹 페이지와 상호작용하는 데 사용됩니다. 에이전트에게 검색된 쿼리를 검색 상자에 입력하도록 지시함으로써 공격자는 자연스럽게 쿼리를 얻을 수 있습니다.

비교를 위해, EHRAgent는 코드 생성을 위해 4개의 레코드를 검색하는 데 편집 거리를 사용하는 반면, RAP는 웹 작업 생성을 위해 3개의 레코드를 검색하는 데 코사인 유사성을 사용합니다.

**Memory Setup.** EHRAgent의 메모리 모듈에 있는 쿼리는 MIMIC-III [[13]](#ref13)의 검증 세트에서 무작위로 선택됩니다. MIMIC-III는 실제 임상 요구에서 수집되었으며 환자에 대한 민감한 데이터를 포함합니다. 그리고 RAP의 메모리에 있는 쿼리는 Amazon 제품에 대한 민감한 사용자 쿼리를 포함하는 Webshop [[41]](#ref41)에서 무작위로 선택됩니다. 우리는 에이전트를 실행하여 이러한 쿼리에 대한 해당 솔루션을 얻으며, 솔루션의 정확성이 개인정보 추출 공격과 관련이 없기 때문에 사용자의 의도된 결과를 성공적으로 달성했는지 여부에 관계없이 수행합니다.