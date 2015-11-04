Version Control:
	v_1.1
		- replaced fixed population by dynamic population
		- the population of the predators only can breed if their numbers are less than half of the population of birds (without that the predators could kill all birs)
	v_1.2:
		- implemented sexual breeding.
		- Best candidate selected by the greater tail


pso_simple:
	modelo simples do PSO, apenas com uma especie (que procura alimentos fixos). Sem perda de energia.

pso_pushEA:
	Com duas especies, uma que procura alimentos fixos e a outra que rouba energia à primeira espécie. Neste modelo já há perda de energia.
	modelo com motor evolucionario em que o modelo cria as suas proprias regras. O motor evolucionario funciona com base no que está na pilha.
	Na reprodução apenas um individuo é criado de cada vez. O numero da população é fixo, ou seja que a reprodução só acontece quando um individuo morre. A selecção dos pais é realizada por um torneio de 5 elementos. Sendo ambos os pais escolhidos globalmente por razões relacionadas com a perda da diversidade.

pso_classicEA:
	Com duas especies, uma que procura alimentos fixos e a outra que rouba energia à primeira espécie. Neste modelo já há perda de energia.
	modelo com motor evolucionario em que se varia os parametos da suma pesada do pso_simple. O motor evolucionario funciona com base na variação dos paramentos da soma pesada.
	Na reprodução dois individuos são criados de cada vez. O numero da população é fixo, ou seja que a reprodução só acontece quando um individuo morre. A selecção dos pais é realizada por um torneio de 5 elementos. Sendo ambos os pais escolhidos globalmente por razões relacionadas com a perda da diversidade.

pso_gpEA:
	Com duas especies, uma que procura alimentos fixos e a outra que rouba energia à primeira espécie. Neste modelo já há perda de energia.
	modelo com motor evolucionario em que é utilizada programação genética para a criação das regras de cada individuo
	Na reprodução dois individuos são criados de cada vez. O numero da população é fixo, ou seja que a reprodução só acontece quando um individuo morre. A selecção dos pais é realizada por um torneio de 5 elementos. Sendo ambos os pais escolhidos globalmente por razões relacionadas com a perda da diversidade.