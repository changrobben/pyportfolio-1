

FMT_TABLE = '''
<table class="table table-condensed table-striped table-hover">
  <thead>
  <tr class="warning">
%s
  </tr>
  </thead>
  <tbody>
%s
  </tbody>
</table>
'''

def gen_data_table(data):
	head = ''
	rows = ''
	for v in data['col_name']:
		head = head + '    <th> %s </th>\n' % v

	for v in data['rows']:
		col = ''
		for field in v:
			col = col + '      <td> %s </td>\n' % field
		rows = rows + '    <tr>\n %s    </tr>\n' % col

	return FMT_TABLE % (head, rows)


print gen_data_table({'col_name':['4','d'], 'rows':[ ['3', 'g'], ['5', 'g']]})

