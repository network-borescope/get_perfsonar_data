# Executando
``python get_full_data.py <src> <dst> <test-type>`` OR ``python get_full_data.py <src> <dst> <test-type> <event-type``

- src: sigla do estado de origem
- dst: sigla do estado de destino
- test-type: deve ser um dos tipos de teste realizado pelo PerfSonar, que são:
  - atraso_bi: Atraso e Perda de Pacotes
  - atraso_uni: Atraso unidirecional
  - traceroute: Traceroute
  - banda_bbr: Banda(BBR)
  - banda_cubic: Banda(CUBIC)

## Exemplos
Pega todos os dados de Banda(BBR) entre os PoPs do Distrito Federal(origem) e São Paulo(destino).

``python get_full_data.py df sp banda_bbr``

Pega todos os dados do evento throughput do teste Banda(BBR) entre os PoPs do Distrito Federal(origem) e São Paulo(destino).

``python get_full_data.py df sp banda_bbr throughput``