"""Gera rastreios.ics a partir dos documentos da colecção "rastreios" (JSON exportados da agenda partilhada).
Uso: python3 -I gerar_ics.py <pasta_com_json> <saida.ics>
Sem telefones nem emails: o ficheiro é publicado num link público."""
import json, glob, sys, os, datetime
EST = {'confirmada':'Confirmada','prereserva':'Pré-reserva','conflito':'Conflito','realizada':'Realizada','cancelada':'Cancelada'}
def esc(t): return str(t).replace('\\', '\\\\').replace(';', r'\;').replace(',', r'\,').replace('\n', r'\n')
def fold(line):
    b = line.encode(); out = []
    while len(b) > 73:
        i = 73
        while (b[i] & 0xC0) == 0x80: i -= 1
        out.append(b[:i].decode()); b = b[i:]
    out.append(b.decode()); return '\r\n '.join(out)
src, dst = sys.argv[1], sys.argv[2]
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Agenda de Rastreios//PT', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
     'X-WR-CALNAME:Rastreios', 'X-WR-TIMEZONE:Africa/Luanda', 'REFRESH-INTERVAL;VALUE=DURATION:PT1H', 'X-PUBLISHED-TTL:PT1H',
     'BEGIN:VTIMEZONE', 'TZID:Africa/Luanda', 'BEGIN:STANDARD', 'DTSTART:19700101T000000', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0100', 'TZNAME:WAT', 'END:STANDARD', 'END:VTIMEZONE']
n = 0
for f in sorted(glob.glob(os.path.join(src, '*.json'))):
    j = json.load(open(f, encoding='utf-8')); e = j.get('data', j); i = j.get('id') or os.path.basename(f)[:-5]
    if e.get('estado') == 'cancelada' or not e.get('datas'): continue
    tot = len(e['datas'])
    for k, d in enumerate(sorted(e['datas'])):
        ds = d.replace('-', '')
        desc = '\n'.join(x for x in [f"ID: {e.get('ref','')}", f"Estado: {EST.get(e.get('estado'),'')}", f"Dia {k+1} de {tot}" if tot > 1 else '',
            f"Responsável operacional: {e['responsavel']}" if e.get('responsavel') else '', f"Equipa: {e['equipa']}" if e.get('equipa') else '',
            f"Espaço: {e['espaco']}" if e.get('espaco') else '', f"Notas: {e['notas']}" if e.get('notas') else ''] if x)
        loc = ', '.join(x for x in [e.get('local'), e.get('morada'), e.get('municipio')] if x)
        L += ['BEGIN:VEVENT', f'UID:{i}-{ds}@agenda-rastreios', f'DTSTAMP:{now}',
              f"DTSTART;TZID=Africa/Luanda:{ds}T{e['inicio'].replace(':','')}00", f"DTEND;TZID=Africa/Luanda:{ds}T{e['fim'].replace(':','')}00",
              fold('SUMMARY:' + esc('Rastreio: ' + e.get('cliente',''))), fold('LOCATION:' + esc(loc)), fold('DESCRIPTION:' + esc(desc)),
              fold('CATEGORIES:' + esc('Rastreio ' + EST.get(e.get('estado'),''))), 'END:VEVENT']
        n += 1
L.append('END:VCALENDAR')
open(dst, 'w', encoding='utf-8', newline='').write('\r\n'.join(L) + '\r\n')
print(n, 'eventos')
