
graph TB
    %% INPUT SOURCES
    subgraph INPUTS["📥 INPUT SOURCES"]
        I1["🏟️ Case Study<br/>Savannah Bananas"]
        I2["📊 Trend Report<br/>Premium Fast Food"]
        I3["📊 Combined Trends<br/>Non-Alcoholic + Sacred Sync"]
        I4["💡 Spotted Innovation<br/>Sexiest Cat Dad Campaign"]
        I5["💡 Spotted Innovation<br/>QR Code Garment Resale"]
    end

    %% PROCESSING PIPELINE
    subgraph PIPELINE["🔄 PROCESSING PIPELINE"]

        subgraph STAGE1["STAGE 1: Input Processing"]
            S1A["🔍 Content Reviewer Expert<br/>Identify Inspirations"]
            S1B["📚 Research Expert<br/>Deep Dive on Inspiration"]
            S1C["📝 Summarize Inspiration<br/>with Supporting Research"]
        end

        subgraph STAGE2["STAGE 2: Signal Amplification"]
            S2A["📱 Social Media Expert<br/>Extract Social Pulse"]
            S2B["📈 Trend Analyst Expert<br/>Extract Related Trends"]
            S2C["🎯 Enhanced Signal Output<br/>with Trend Context"]
        end

        subgraph STAGE3["STAGE 3: General Translation"]
            S3A["💼 Innovation Agency Expert<br/>Extract Universal Lessons"]
            S3B["🔑 Key Takeaways<br/>De-contextualized Principles"]
        end

        subgraph STAGE4["STAGE 4: Brand Contextualization"]
            S4A["🔬 Expert Researcher<br/>Deep Brand Research"]
            S4B["💼 Innovation Agency Expert<br/>Customize for Brand Context"]
            S4C["🎨 Brand-Specific<br/>Strategic Insights"]
        end

        subgraph STAGE5["STAGE 5: Opportunity Generation"]
            S5A["💼 Innovation Agency Expert<br/>Identify Top 2 Opportunities"]
            S5B["🎨 Content & Visual Expert<br/>Create Opportunity Cards"]
            S5C["⚙️ Prompt Engineer<br/>Generate Follow-up Prompts"]
        end
    end

    %% BRAND CONTEXT DATABASE
    subgraph BRANDS["🏢 BRAND CONTEXT PROFILES"]
        B1["🥛 Lactalis Canada<br/>Dairy Products<br/>(Milk, Cheese, Yogurt)"]
        B2["🌶️ McCormick USA<br/>Condiments & Spices"]
        B3["⛰️ Columbia<br/>Outdoor Gear"]
        B4["🏃 Decathlon<br/>Sporting Goods Retail"]
    end

    %% OUTPUTS
    subgraph OUTPUTS["📤 OUTPUTS - Opportunity Cards"]
        O1["📋 Opportunity Card 1<br/>Visual + Description"]
        O2["📋 Opportunity Card 2<br/>Visual + Description"]
        O3["🔮 Follow-up Prompts<br/>for Further Development"]
    end

    %% TEST MATRIX
    subgraph TESTMATRIX["🧪 TEST MATRIX (20 Tests)"]
        T1["Test 1-4: Savannah Bananas<br/>→ All 4 Brands"]
        T2["Test 5-8: Premium Fast Food<br/>→ All 4 Brands"]
        T3["Test 9-12: Combined Trends<br/>→ All 4 Brands"]
        T4["Test 13-16: Cat Dad Campaign<br/>→ All 4 Brands"]
        T5["Test 17-20: QR Garment Resale<br/>→ All 4 Brands"]
    end

    %% VALIDATION METRICS
    subgraph VALIDATION["✅ SUCCESS VALIDATION"]
        V1["⏱️ Speed: Pipeline Execution Time"]
        V2["⭐ Quality: Novelty & Actionability"]
        V3["🎯 Relevance: Brand Fit Authenticity"]
        V4["📊 Specificity: Implementation Detail"]
        V5["🔀 Differentiation: Unique Outputs per Brand"]
    end

    %% FLOW CONNECTIONS
    I1 --> S1A
    I2 --> S1A
    I3 --> S1A
    I4 --> S1A
    I5 --> S1A

    S1A --> S1B --> S1C
    S1C --> S2A
    S2A --> S2B --> S2C
    S2C --> S3A --> S3B

    S3B --> S4A
    B1 --> S4A
    B2 --> S4A
    B3 --> S4A
    B4 --> S4A

    S4A --> S4B --> S4C
    S4C --> S5A --> S5B --> S5C

    S5C --> O1
    S5C --> O2
    S5C --> O3

    O1 --> TESTMATRIX
    O2 --> TESTMATRIX
    O3 --> TESTMATRIX

    TESTMATRIX --> VALIDATION

    %% STYLING
    classDef inputStyle fill:#e1f5ff,stroke:#0066cc,stroke-width:2px
    classDef stageStyle fill:#fff4e6,stroke:#ff9800,stroke-width:2px
    classDef brandStyle fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef outputStyle fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    classDef testStyle fill:#fff3e0,stroke:#ff6f00,stroke-width:2px
    classDef validationStyle fill:#fce4ec,stroke:#e91e63,stroke-width:2px

    class I1,I2,I3,I4,I5 inputStyle
    class S1A,S1B,S1C,S2A,S2B,S2C,S3A,S3B,S4A,S4B,S4C,S5A,S5B,S5C stageStyle
    class B1,B2,B3,B4 brandStyle
    class O1,O2,O3 outputStyle
    class T1,T2,T3,T4,T5 testStyle
    class V1,V2,V3,V4,V5 validationStyle
    

---- Links
https://mermaid.live/edit#pako:eNqVV9tu48YZfpUBgyy2CLURT7JMFAtIlGwIsSWvSTsn52JMDqXBUiTDg21lsUCBJkHQJnGyuzfZbbBI0UWKoqe9KXrRp_ELtI_QfzgkRVL02pFhaA7_fDP_9x_1SLADhwi6MI9wuEDW8MRH8Hn7bTSZHhxZyJwdHRpjk6_G6SkXy_bMj0-E_718-qohKXzChdlnImUyly__--9LZOCYIDNJndWvT6N375v4DPs-XqAh9uEvrh-UOfjvkBUR30GHJAyiJDt3EJElTZdoB8cJ2gkCp35QKQ4awfKU-sThCHF2dhr4nYFnB4vAozZ6B5nYjkDCXPl2HUXNUJ78hMwwSBIQmfh-cIYTGvj88eSCErjfwAkaYQe-lyGmc7-Oot2A8uAQXukQtIujJfET0DLGHikx4NknfmmPg8MZ0GtOprvoYHIw3ptMxw2rFMvZrc8-bz3BsNcvLI-a1mB3zIyVDZCkw1PDNEEHUWCTOKb-vKYZ-5jSgF_0DSjhJ_z9Z5SckwiNL0KSm2viwA51VwAYhzTKlI9bwIbcbs8ZCQRH9qIKMiIkRCN6RlDgV4FacAyO8yMy0-USR_QzUj2QoZ3TBDROQ-ZSoFl5Yw2tQv4mU3LJlKwjE-yOPTRYhh51qX3Nw2TO1tPXyAxsCvL7xKG4quT4IomwnRT7B6kXkxacnKiv8sgYwN0r8MQWoEPi4aQMgBYoztW3_0Bjf4F9m0UC12WWJmD9NVn8qszMF8ntaVJKmhQd7RKfRIBtRdiPvWtYUjhLT_5TCRU0mBPfXrVpeOSDT0QQNGgPvLTVsRTO17Pv0XtkhSz8kOBzvIpzt-rYXKcUe-ApDvg79W0aeiS-vZZqqaWqoyFoVzKVoV6jqZpHz19zvUovJNHa5Tlaq39ykOGt6DLSOAmWLBTcIKo_sQUz94o_c8GOGRKb-TXPe8B7QuaQPCGo6HyR_AKetJInTUezLPpSnyar3DPaadJu5xBllrGCEMkVdEpafEIbFioWmesOOqYxmKvGWkRA19pLDRy1BZLGKLt6_gOrcpAxlyGEoz-H4pPbMleQQLnyvOC8k4a5WAt7m4l_eDiYjpAxm1rjDyw0GliD4cBs5v5MiFfkyz82jkAd2JnsNUrzkJfmVy_QHkQSOGoM2vnYwdz7MI1W7JFOaic8WO7uU--hiIwFAXcU0YfBPI2SX9UxedX--l-MiH3bCKIltR-iI3PACQ18h7JCFwPfZkjthm2GLF9cvfhn1iwEXgr1m78G0pETgOfuQhjUT_A6fflbNCKQeBdeUZ6L1L4L_UEMAZRg6l1TV2dHFmtmGnzmqzzX_qmYos4N7jDjrD79_YYckrKX5W72Djw4tiMabnj9TL4WQb4lAm-Bnv19090yAJYDdsB2kGkA44x4QciMcg091ti00P7AOpx80KCI7fCN7L6f_1KVRXflLrKgRYrrLmIxgtg6kjqQLptNYPbAqy-foIHnIZVnoDrDllwAaJ2-jja6wVsgKAXCdkeC-t3WKL4ZQC11UDpST9_oAm8BoZUQWx25qyNoBetd4Jsx6jY6HuxNIC9MZlO0Pwb2jaY3rwVYhP3hC2QeGaw1rGzUnnfMrHR1-ZpFIuR_4gDRNCQe0AQZkthploYtCOb6MWabq799hx6wypesdDQNwL_Af--ggc3O4FPKNuqnlKINgYaFnLFGpKijOzRBgxQ8FZK7vXFOLVr9okRlV06gDyOMSF4rRvXYzw7yvvzZb6CldF0SMfRMWGcNxacpyfufGEEt4C-5hvidvdn7LM1OxwbjMKd9IqFO5z5rkPO53JgrjbnamGvrOV-BYb40zL-NYsPgC3J-Fgb5Qi4pF5JyLqnkAsqwRFdyWTUHGUqNudyYK425up7nkGp-i1pAF89Q82douYCWC2hGeVbjIjOpMZcbc6U4MePvXSekfFluX1Y2lvnGeiUTqMTG2uKm9SH8jtrlc9vDcTwiLqLsx5KZrDzosKjn6W8RydVcV4yTKHhI9Le63V7PtvNp55w6yUKXw4sGSpzgOamiuK6rkl6J4rrb_W73JpRT5q81FIVorlaibNvy1umNKEEWATWV-q5GtksY1caudiNMAimuoZFCuhWNeu7NGp1BMnGyAK1B2UQldglFtiXSU1qgKmAQmeJEFieKOFFFiLK12apCEGwiBBr8GyKEE_zDWIaxAmMFxip8q-wb1jQYazAGn1ybr4o2lMShLA4VEYJkbZqqxEwSZ7IIXlnhvLpvSaIli5YiWqpoaWtKqzLHkngsi8eKeKyKx1qTMS4piMI8oo6gJ1FKRGFJoiVmU-ER2z8RIM2yfK7D0CEuTj1oCU78x3AsxP5HQbAsTkZBOl8IuovhB6oopCHcREYUQ6lZlquslJLICFI_EfT-dj8DEfRHwoWgd9T-ve7WVlfR5F5vu6-qmiisYLnf7d_r9aV-b0vTuqqs9h-LwmfZvfK9ntLb6sqSrPRUubvde_x_aLbitg