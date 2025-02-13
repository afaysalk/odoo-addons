# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

to_19_fr = (u'Zéro', 'Un', 'Deux', 'Trois', 'Quatre', 'Cinq', 'Six',
            'Sept', 'Huit', 'Neuf', 'Dix', 'Onze', 'Douze', 'Treize',
            'Quatorze', 'Quinze', 'Seize', 'Dix-sept', 'Dix-huit', 'Dix-neuf')
tens_fr = ('Vingt', 'Trente', 'Quarante', 'Cinquante', 'Soixante',
           'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
denom_fr = ('',
            'Mille', 'Millions', 'Milliards', 'Billions', 'Quadrillions',
            'Quintillion', 'Sextillion', 'Septillion', 'Octillion', 'Nonillion',
            'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
            'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')


def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if val % 10:
                if dval == 70 or dval == 90:
                    return tens_fr[int(dval / 10 - 3)] + '-' + to_19_fr[val % 10 + 10]
                else:
                    return dcap + '-' + to_19_fr[val % 10]
            return dcap


def _convert_nnn_fr(val):
    """ convert a value < 1000 to french

        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = 'Cent'
        else:
            word = to_19_fr[rem] + ' Cent'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word


def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
        return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1:
                ret = denom_fr[didx]
            else:
                ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ', ' + french_number(r)
            return ret


def amount_to_text_fr(numbers, currency):
    number = '%.2f' % numbers
    units_name = currency
    liste = str(number).split('.')
    start_word = french_number(abs(int(liste[0])))
    end_word = french_number(int(liste[1]))
    cents_number = int(liste[1])
    cents_name = (cents_number > 1) and ' Centimes' or ' Centime'
    final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
    return final_result


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    amount_to_text = fields.Text(string='In Words',
                                 store=True, readonly=True, compute='_amount_in_words')

    @api.depends('amount_total')
    def _amount_in_words(self):
        for record in self:
            record.amount_to_text = amount_to_text_fr(
                record.amount_total, record.currency_id.symbol)


class SaleOrderAmountToText(models.Model):
    _inherit = "sale.order"

    amount_to_text = fields.Text(string='In Words',
                                 store=True, readonly=True, compute='_amount_in_words')

    @api.depends('amount_total')
    def _amount_in_words(self):
        self.amount_to_text = amount_to_text_fr(
            self.amount_total, self.pricelist_id.currency_id.symbol)


class AccountInvoice(models.Model):
    _inherit = "account.move"
   
    amount_to_text = fields.Text(string='In Words',
        store=True, readonly=True, compute='_amount_in_words')
    
    @api.depends('amount_total')
    def _amount_in_words(self):
        self.amount_to_text = amount_to_text_fr(self.amount_total, self.currency_id.symbol)
