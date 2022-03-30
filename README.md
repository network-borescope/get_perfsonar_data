# Executando
``python get_full_data.py --time-start <time-start> --test-type <test-type> --time-end <time-end>(opcional) <event-type>(opcional)``

- time-start: Data a partir da qual os dados serao pegos, deve estar no formato YYYYMMDD
- time-end: date até a qual os dados serao pegos(inclusivo). 20210626 pegara dados ate 26/06/2021 23:59:59
- test-type: deve ser um dos tipos de teste realizado pelo PerfSonar, que são:
  - atraso_bidir: Atraso e Perda de Pacotes
  - atraso_uni: Atraso unidirecional
  - traceroute: Traceroute
  - banda_bbr: Banda(BBR)
  - banda_cubic: Banda(CUBIC)

## Exemplos
Pega todos os dados de Banda(BBR) a partir de 01/06/2021.

``python3 get_full_data.py --time-start 20210601 --test-type banda_bbr``

Pega todos os dados do evento throughput do teste Banda(BBR) a partir de 01/06/2021.

``python3 get_full_data.py --time-start 20210601 --test-type banda_bbr --event-type throughput``