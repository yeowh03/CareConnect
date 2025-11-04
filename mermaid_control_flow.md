# Mermaid Control Flow Graphs

## create_request() Method Control Flow

```mermaid
flowchart TD
    N1["1. START"] --> N2["2. Get Current User"]
    N2 --> N3{"3. User Authenticated?"}
    N3 -->|No| N4["4. Return 401 Unauthorized"]
    N3 -->|Yes| N5["5. Parse JSON Data"]
    N5 --> N6{"6. Category Valid?"}
    N6 -->|No| N7["7. Return 400 Category Required"]
    N6 -->|Yes| N8{"8. Item Valid?"}
    N8 -->|No| N9["9. Return 400 Item Required"]
    N8 -->|Yes| N10["10. Try Parse Quantity"]
    N10 --> N11{"11. Quantity > 0?"}
    N11 -->|No| N12["12. Raise ValueError"]
    N12 --> N13["13. Catch Exception"]
    N13 --> N14["14. Return 400 Quantity Invalid"]
    N11 -->|Yes| N15{"15. Location Valid?"}
    N15 -->|No| N16["16. Return 400 Location Required"]
    N15 -->|Yes| N17["17. Try Database Operations"]
    N17 --> N18["18. Create Request Object"]
    N18 --> N19["19. Add to Session"]
    N19 --> N20["20. Commit Transaction"]
    N20 --> N21["21. Run Allocation"]
    N21 --> N22["22. Broadcast to CC"]
    N22 --> N23["23. Return 201 Created"]
    N17 -->|Exception| N24["24. Catch DB Exception"]
    N24 --> N25["25. Rollback Transaction"]
    N25 --> N26["26. Return 500 Database Error"]
    
    %% Styling
    classDef startEnd fill:#e1f5fe
    classDef decision fill:#fff3e0
    classDef error fill:#ffebee
    classDef success fill:#e8f5e8
    classDef process fill:#f3e5f5
    
    class N1,N23 startEnd
    class N3,N6,N8,N11,N15 decision
    class N4,N7,N9,N14,N16,N26 error
    class N23 success
    class N2,N5,N10,N17,N18,N19,N20,N21,N22,N12,N13,N24,N25 process
```

## reject_matched_request() Method Control Flow

```mermaid
flowchart TD
    N1["1. START"] --> N2["2. Get Current User"]
    N2 --> N3{"3. User Authenticated?"}
    N3 -->|No| N4["4. Return 401 Unauthorized"]
    N3 -->|Yes| N5["5. Parse JSON Data<br/>i, location, r"]
    N5 --> N6{"6. All Fields Present?"}
    N6 -->|No| N7["7. Return 400 Fields Required"]
    N6 -->|Yes| N8["8. Query Request by ID"]
    N8 --> N9{"9. Request Exists?"}
    N9 -->|No| N10["10. Return 404 Not Found"]
    N9 -->|Yes| N11{"11. User Owns Request?"}
    N11 -->|No| N12["12. Return 403 Forbidden"]
    N11 -->|Yes| N13{"13. Status = Matched?"}
    N13 -->|No| N14["14. Return 400 Invalid Status"]
    N13 -->|Yes| N15["15. Try Database Operations"]
    N15 --> N16["16. Get Reservations"]
    N16 --> N17["17. For Each Reservation:<br/>- Get Item<br/>- Set Available<br/>- Delete Reservation"]
    N17 --> N18["18. Delete Request"]
    N18 --> N19["19. Commit Transaction"]
    N19 --> N20["20. Run Allocation"]
    N20 --> N21["21. Return 200 Success"]
    N15 -->|Exception| N22["22. Catch DB Exception"]
    N22 --> N23["23. Rollback Transaction"]
    N23 --> N24["24. Return 500 Database Error"]
    
    %% Styling
    classDef startEnd fill:#e1f5fe
    classDef decision fill:#fff3e0
    classDef error fill:#ffebee
    classDef success fill:#e8f5e8
    classDef process fill:#f3e5f5
    
    class N1,N21 startEnd
    class N3,N6,N9,N11,N13 decision
    class N4,N7,N10,N12,N14,N24 error
    class N21 success
    class N2,N5,N8,N15,N16,N17,N18,N19,N20,N22,N23 process
```

## Side-by-Side Comparison

```mermaid
flowchart LR
    subgraph CR["create_request()"]
        CR1[Auth Check] --> CR2[Field Validation]
        CR2 --> CR3[Create & Save]
        CR3 --> CR4[Success 201]
    end
    
    subgraph RMR["reject_matched_request()"]
        RMR1[Auth Check] --> RMR2[Field + Business Validation]
        RMR2 --> RMR3[Delete & Cleanup]
        RMR3 --> RMR4[Success 200]
    end
    
    CR1 -.->|Same Pattern| RMR1
    CR4 -.->|Different Operations| RMR4
    
    classDef createStyle fill:#e3f2fd
    classDef rejectStyle fill:#fce4ec
    
    class CR1,CR2,CR3,CR4 createStyle
    class RMR1,RMR2,RMR3,RMR4 rejectStyle
```

## Cyclomatic Complexity Visualization

```mermaid
graph TD
    subgraph "Decision Points Analysis"
        A[Entry Point] --> B[Decision 1: Auth]
        B --> C[Decision 2: Validation 1]
        C --> D[Decision 3: Validation 2]
        D --> E[Decision 4: Validation 3]
        E --> F[Decision 5: Validation 4]
        F --> G[Decision 6: Exception Handling]
        G --> H[Exit Points]
    end
    
    I[Cyclomatic Complexity<br/>V(G) = E - N + 2P<br/>V(G) = 6 + 1 = 7]
    
    classDef complexity fill:#fff9c4
    class I complexity
```

## Path Coverage Matrix

```mermaid
graph LR
    subgraph "Test Paths"
        P1[Path 1: 401 Unauthorized]
        P2[Path 2: 400 Validation Error 1]
        P3[Path 3: 400 Validation Error 2]
        P4[Path 4: 400 Validation Error 3]
        P5[Path 5: 400 Validation Error 4]
        P6[Path 6: 500 Database Error]
        P7[Path 7: Success Path]
    end
    
    subgraph "Coverage"
        C1[100% Decision Coverage]
        C2[100% Branch Coverage]
        C3[100% Path Coverage]
    end
    
    P1 --> C1
    P2 --> C1
    P3 --> C1
    P4 --> C2
    P5 --> C2
    P6 --> C2
    P7 --> C3
    
    classDef pathStyle fill:#e8f5e8
    classDef coverageStyle fill:#e1f5fe
    
    class P1,P2,P3,P4,P5,P6,P7 pathStyle
    class C1,C2,C3 coverageStyle
```