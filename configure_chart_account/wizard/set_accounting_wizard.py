# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jorge Angel Naranjo(jorge_nr@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class set_accounting_data_wizard(osv.osv_memory):
    _name = 'set.accounting.data.wizard'
    
    _columns={
        'account_ids' : fields.many2many('account.account',
            'account_account_partner_rel', 'parent_id', 'account_id',
            'Account'),
        'parent_id': fields.many2one('account.account', 'Parent',
            ondelete='cascade', domain=[('type','=','view')], required=True),
        'create_journal': fields.boolean('Create Journals?')
    }

    def set_accounting_company(self, cr, uid, ids, context=None):
        '''
        This wizard assigns a partner account and change your account
        type to root/view .
        '''
        journal_obj = self.pool.get('account.journal')
        obj_wizard = self.browse(cr, uid, ids[0])
        account_id = obj_wizard.account_ids
        form = self.read(cr, uid, ids, context=context)
        if obj_wizard.create_journal:
            cr.execute("""
                SELECT 
                    nivel.id,
                    nivel.name,
                    nivel.type,
                    nivel.company_id
                    FROM
                    ( SELECT node.company_id,node.type,node.id as id,node.name
                        FROM account_account AS node,account_account AS parent
                        WHERE node.parent_left BETWEEN parent.parent_left
                        AND parent.parent_right
                        AND parent.id = %s
                        ORDER BY parent.parent_left ) nivel
                    WHERE nivel.id<> %s
                    AND nivel.type <> 'view'
                  """,(obj_wizard.parent_id.id, obj_wizard.parent_id.id,))
            dat = cr.dictfetchall()
            for acc_j in dat:
                journal_obj.create(cr, uid, {
                    'name': acc_j['name'],
                    'code': str(acc_j['id']),
                    'type': 'bank',
                    'default_debit_account_id': acc_j['id'],
                    'default_credit_account_id': acc_j['id'],
                })
        else:
            account_ids = form[0]['account_ids']
            cr.execute("""
                UPDATE account_account SET type='view' WHERE id IN
                (SELECT DISTINCT id
                    FROM account_account WHERE type <> 'view' AND id IN
                        (SELECT DISTINCT parent_id FROM account_account
                            WHERE parent_id IS NOT NULL))""")
            for acc in account_ids:
                self.pool.get('account.account').write(cr, uid, [acc],
                    {'parent_id': obj_wizard.parent_id.id})
        return False
    
