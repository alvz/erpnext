# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import webnotes
import webnotes.model
from webnotes.utils import flt
from webnotes.model.controller import getlist
from webnotes.model.controller import DocListController
	
def get_balance_on(account, dt):
	acc = webnotes.conn.get_value('Account', account, \
		['lft', 'rgt', 'debit_or_credit', 'is_pl_account'], as_dict=1)
	cond = ""
	if acc['is_pl_account'] == 'Yes':
		year_start_date = webnotes.conn.sql("select year_start_date from `tabFiscal Year` \
			where year_start_date < %s order by year_start_date limit 1", dt)
		year_start_date = year_start_date and year_start_date[0][0] or ''
		cond += " and posting_date >= %s" % year_start_date
		
	bal = webnotes.conn.sql("""
		SELECT sum(ifnull(debit, 0)) - sum(ifnull(credit, 0)) 
		FROM `tabGL Entry`
		WHERE account in (select name from `tabAccount` where lft >= %s and rgt <= %s) 
		AND posting_date <= %s %s
	""", (acc['lft'], acc['rgt'], dt, cond))[0][0]
	
	if acc['debit_or_credit'] == 'Credit':
		bal = -bal
	return bal
	
def add_account(args):
	args.update({"doctype": "Account"})
	return webnotes.model.insert(args)

def add_cost_center(args):
	args.update({"doctype": "Cost Center"})
	return webnotes.model.insert(args)

class GLController(DocListController):
	def make_gl_entries(self, mappers):
		for each in mappers:
			for fld in mappers[each]:
				if fld.get('table_field'):
					for row in getlist(obj.doclist, fld.get('table_field')):
						if fld.get('table_field') != 'purchase_tax_details' or row.get('category') != 'For Valuation':
							self.make_single_gl_entry(mappers[each], child_obj = row)
				else:
					self.make_single_gl_entry(mappers[each])
					
		self.validate_total_debit_credit()

	def make_single_gl_entry(self, mapper, child_obj):
		gle = {}
		for k in mapper:
			gle[k] = self.get_value(mapper[k], child_obj)
		
		if flt(gle['debit']) < 0 or flt(gle['credit']) < 0:
			tmp=gle['debit']
			gle['debit'], gle['credit'] = abs(flt(gle['credit'])), abs(flt(tmp))
		
		# insert gl entry
		webnotes.model.insert_variants('GL Entry', [gle])
		
		# add to total_debit, total_credit
		self.total_debit += flt(gle['debit'])
		self.total_credit += flt(gle['credit'])
		
	def get_value(self, fld, child_obj):
		if fld.startswith('par:'):
			return self.doc.get(fld[4:])
		else:
			return child_obj.get(fld)
		
	def validate_total_debit_credit(self):
		if abs(self.total_debit - self.total_credit) > 0.001:
			msgprint("Debit and Credit not equal for this voucher: Diff(Dr) is %s" 
				% (self.total_debit - self.total_credit), raise_exception=webnotes.ValidationError)
				
	def delete_gl_entries(self):
		webnotes.conn.sql("delete from `tabGL Entry` where voucher_type = %s \
			and voucher_no = %s", (self.doc.doctype, self.doc.name))