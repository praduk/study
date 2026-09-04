Name the clauses

$$C_1=p\lor q,\quad C_2=\neg p\lor r,\quad C_3=\neg q\lor r,\quad C_4=\neg r.$$

Resolve $C_1$ with $C_2$ on $p$ to obtain $C_5=q\lor r$. Resolve $C_5$ with $C_4$ on $r$ to obtain $C_6=q$. Resolve $C_3$ with $C_4$ on $r$ to obtain $C_7=\neg q$. Finally resolve $C_6$ with $C_7$ on $q$ to obtain the empty clause. This is a resolution refutation, so resolution soundness proves that the original set is unsatisfiable.
