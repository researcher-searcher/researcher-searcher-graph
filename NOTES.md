## Queries

Find similar people who don't share an output

```
match (p1:Person)-[pp:PERSON_PERSON]-(p2) where p1.email contains 'tom.gaunt' with p1,pp,p2 order by pp.score desc limit 1000 match (p2) where not (p1)-[:PERSON_OUTPUT]-(:Output)-[:PERSON_OUTPUT]-(p2) return p2.name,pp.score order by pp.score desc limit 10 ;
```

Find similar outputs

```
match (o1:Output)-[r:OUTPUT_OUTPUT]-(o2:Output) where r.score>0.98 with o1,r,o2 limit 5 match (o1)-[po1:PERSON_OUTPUT]-(p1:Person) match (o2)-[po2:PERSON_OUTPUT]-(p2:Person) return o1,r,o2,p1,p2,po1,po2
```