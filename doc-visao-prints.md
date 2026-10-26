# Automação para comprovação no Portal
Existe um produto comercializado pela rádio que é veiculado no portal chamado **BANNER**, ao final da veiculação é preciso ser produzido um documento que comprove que o BANNER do cliente realmente esteve presente no portal em determinado periodo.

 Hoje quem executa esse movimento é o _Social Media_ do Setor de `Criação`, gastando tempo em uma tarefa que pode ser automatizada.

## Regras de Négocio

| ID | Regra |
|:----|:-------|
|RN01| É necessário está aparente a barra de ferramentas do S.O, para comprovarar o data e hora em que foi tirado o PRINT|
|RN02| É necessário está aparente o endereço completo do SITE (URL)|
|RN03| O documento deve conter 2 prints por semana de veiculação. Ex.: Um banner com 1 MÊS de veiculação vai gerar um documento com 8 PRINTS|

## Requisitos Funcionais
|ID| Nome| Descrição |
|:-|:-|:-|
|RF01| Listar Banner | O sistema deve listar os banners que estão sendo monitados |
|RF02| Listar Prints | O sistema deve listar os prints feitos de cada banner separado por clientes |
|RF03| Listar documentos | O sistema deve mostrar uma lista (Nome Banner, Inicio Veiculação, Fim Veiculação,  ) dos documentos produzido |
