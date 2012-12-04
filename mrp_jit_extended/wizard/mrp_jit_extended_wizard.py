# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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
from osv import osv, fields
from tools.translate import _
import netsvc

class procurement_order_merge_jit_extended(osv.osv_memory):
    _name = 'procurement.order.merge.jit.extended'

    def procurement_merge_jit(self, cr, uid, ids, context=None, rec_ids=None):
        procurement_order_pool = self.pool.get('procurement.order')
        mrp_production_pool = self.pool.get('mrp.production')
        if context is None:
            context = {}
        if rec_ids is None:
            production_ids = context.get('active_ids', [])
        else:
            production_ids = rec_ids
        procurement_ids = []
        print production_ids, "production ids ke llamaron este --comienzo del ciclo"
        for production_id in production_ids:
            production_data = mrp_production_pool.browse(cr, uid, production_id, context=context)
            for line in production_data.procurement_ids:
                if (line.state == 'draft') and (line.product_id.supply_method=='produce'):
                    procurement_ids.append(line.id)

        res = procurement_order_pool.do_merge(cr, uid, procurement_ids, context=context)
        #append the procurements that are not in draft still
        draft_procurements = procurement_order_pool.browse(cr, uid, procurement_ids, context=context)
        for line in draft_procurements:
            print line.state, "line state"
            print line.product_id.supply_method, "suppky method"
            if (line.state == 'draft') and (line.product_id.supply_method=='produce') and (line.product_id.type <> 'service'):
                res.append(line.id)
        #forwards procurements that were merged
        wf_service = netsvc.LocalService("workflow")
        new_ids = []
        print res, "<- res"
        #for production_id in production_ids:
        #    production_data = mrp_production_pool.browse(cr, uid, production_id, context=context)
        #    for line in production_data.procurement_ids:
        #        if (line.state == 'draft') and (line.product_id.supply_method=='produce') and (line.product_id.type <> 'service'):
        for line in res:
            wf_service.trg_validate(uid, 'procurement.order', line, 'button_confirm', cr)
            wf_service.trg_validate(uid, 'procurement.order', line, 'button_check', cr)
            procurements = self.pool.get('procurement.order').read(cr, uid, line, ['production_created'], context=context)
            new_production_id = procurements.get('production_created')
            print new_production_id, "<- new production id"
            print "2 veces?\n"
            if new_production_id:
                new_ids.append(new_production_id[0])
                        #new_production_id = new_production_id_tup[0]
                        #res[0].append(new_production_id)

        print new_ids, "<- new_ids\n"
        if new_ids:
        #    for line in res[1]:
            #mrp_production_pool.write(cr, uid, new_ids, {'subproduction_ids': [(4, production_ids)]})
            self.procurement_merge_jit(cr, uid, ids, context, new_ids)
        return {}

procurement_order_merge_jit_extended()
