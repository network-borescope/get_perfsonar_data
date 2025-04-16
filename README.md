# Executando
``python3 get_full_data.py --time-start <time-start> --test-type <test-type> --time-end <time-end>(opcional) <event-type>(opcional) --raw-data(opcional)``

- sources: Lista de origens da medição separado por vírgula.
- destinations: Lista de destinos da medição separado por vírgula. (ignorado nos test-type http e dns)
- time-start: Data a partir da qual os dados serão coletados, deve estar no formato YYYYMMDD
- time-end: Data até a qual os dados serão coletados(inclusivo). 20250413 coletará dados até 13/04/2025 23:59:59
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
Coleta todos os dados (brutos) de Atraso Bidirecional a partir de 13/04/2025 para as origens POP-RJ, POP-SP e destinos POP-SC, POP-RJ.

``python3 get_full_data.py --time-start 20250413 --test-type atraso_bidir --sources 'rj,sp' --destinations 'sc,rj' --raw-data``

Coleta todos os dados (brutos) do evento histogram-rtt do teste Atraso Bidirecional a partir de 13/04/2025 para as origens POP-RJ, POP-SP e destinos POP-SC, POP-RJ.

``python3 get_full_data.py --time-start 20250413 --event-type histogram-rtt --test-type atraso_bidir --sources 'rj,sp' --destinations 'sc,rj' --raw-data``

Coleta os dados brutos do teste traceroute de 12/04/2025 até 14/04/2025 para as origens POP-RJ, POP-SP e destinos POP-SC, POP-RJ.

``
python3 get_full_data.py --time-start 20250413 --time-end 20250414 --test-type traceroute --sources 'rj,sp' --destinations 'sc,rj' --raw-data
``
