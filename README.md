# Executando
``python3 get_full_data.py --time-start <time-start> --test-type <test-type> --time-end <time-end>(opcional) <event-type>(opcional) --raw-data(opcional)``

- time-start: Data a partir da qual os dados serão coletados, deve estar no formato YYYYMMDD
- time-end: Data até a qual os dados serão coletados(inclusivo). 20210626 coletará dados até 26/06/2021 23:59:59
- test-type: Deve ser um dos tipos de teste realizado pelo PerfSonar, que são:
  - atraso_bidir: Atraso e Perda de Pacotes
  - atraso_uni: Atraso unidirecional
  - traceroute: Traceroute
  - banda_bbr: Banda(BBR)
  - banda_cubic: Banda(CUBIC)
  - http: HTTP
  - dns: DNS
- event-type: Deve ser utilizado quando deseja-se coletar um evento específico de determinado teste.
- raw-data: Uma flag que se presente faz com que os dados coletados não sejam convertidos para o padrão usado pelo Tinycubes, mantendo o dado bruto.

## Exemplos
Coleta todos os dados de Banda(BBR) a partir de 01/06/2021.

``python3 get_full_data.py --time-start 20210601 --test-type banda_bbr``

Coleta todos os dados do evento throughput do teste Banda(BBR) a partir de 01/06/2021.

``python3 get_full_data.py --time-start 20210601 --test-type banda_bbr --event-type throughput``

Coleta os dados brutos do teste traceroute de 01/10/2021 até 31/10/2021.

``
python3 get_full_data.py --test-type traceroute --time-start 20211001 --time-end 20211031 --raw-data
``