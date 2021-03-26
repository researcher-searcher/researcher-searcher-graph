## Queries

```
match (p1:Person)-[pp:PERSON_PERSON]-(p2) where p1.email contains 'tom.gaunt' with p1,pp,p2 order by pp.score desc limit 1000 match (p2) where not (p1)-[:PERSON_OUTPUT]-(:Output)-[:PERSON_OUTPUT]-(p2) return p2.name,pp.score order by pp.score desc limit 10 ;
```