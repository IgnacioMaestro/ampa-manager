from datetime import datetime
from decimal import Decimal

from xsdata.models.datatype import XmlDate

from .group_header_creator import GroupHeaderCreator
from .postal_address_creator import PostalAddressCreator
from ..receipt import Receipt
from ..remittance import Remittance
from ..sepa.xml_pain_008_001_02 import Document, CustomerDirectDebitInitiationV02, PaymentInstructionInformation4, \
    PartyIdentification32, Party6Choice, PaymentMethod2Code, PaymentTypeInformation20, ServiceLevel8Choice, \
    LocalInstrument2Choice, SequenceType1Code, PostalAddress6, CashAccount16, AccountIdentification4Choice, \
    BranchAndFinancialInstitutionIdentification4, FinancialInstitutionIdentification7, PersonIdentification5, \
    GenericPersonIdentification1, PersonIdentificationSchemeName1Choice, DirectDebitTransactionInformation9, \
    PaymentIdentification1, ActiveOrHistoricCurrencyAndAmount, DirectDebitTransaction6, MandateRelatedInformation6, \
    GenericFinancialIdentification1, RemittanceInformation5, GroupHeader39
from ...dynamic_settings.dynamic_settings import DynamicSetting


class DocumentCreator:
    COUNTRY = 'ES'
    CORE = 'CORE'
    EURO = 'EUR'
    SEPA = 'SEPA'
    party_identification: str
    generic_organisation_identification_id: str

    def __init__(self, remittance: Remittance):
        self.remittance = remittance
        self.party_identification = DynamicSetting.load().remittances_party_id
        self.generic_organisation_identification_id = DynamicSetting.load().remittances_generic_org_id

    def create(self) -> Document:
        return Document(cstmr_drct_dbt_initn=self.create_customer_direct_debit_initiation())

    def create_customer_direct_debit_initiation(self) -> CustomerDirectDebitInitiationV02:
        group_header: GroupHeader39 = GroupHeaderCreator(
            remittance=self.remittance, party_identification=self.party_identification,
            organization_id=self.generic_organisation_identification_id).create()
        payment_information: list[PaymentInstructionInformation4] = self.create_payment_information_list()
        return CustomerDirectDebitInitiationV02(grp_hdr=group_header, pmt_inf=payment_information)

    def create_payment_information_list(self) -> list[PaymentInstructionInformation4]:
        payment_instruction_information = PaymentInstructionInformation4(
            pmt_inf_id=self.remittance.sepa_id, pmt_mtd=PaymentMethod2Code.DD,
            nb_of_txs=str(len(self.remittance.obtain_receipts_grouped_by_iban())),
            ctrl_sum=Decimal(format(self.remittance.calculate_total_amount(), '.2f')), btch_bookg=True,
            pmt_tp_inf=self.create_payment_type_information(), reqd_colltn_dt=self.create_payment_date(),
            cdtr=self.create_party_identification_cdtr(), cdtr_acct=self.create_cash_account(),
            cdtr_agt=self.create_branch_and_financial_institution_id(),
            cdtr_schme_id=self.create_party_identification_ctr_scheme(),
            drct_dbt_tx_inf=self.create_direct_debit_transaction_informations())
        return [payment_instruction_information]

    def create_direct_debit_transaction_informations(self) -> list[DirectDebitTransactionInformation9]:
        receipts_by_iban: list[Receipt] = self.remittance.obtain_receipts_grouped_by_iban()
        direct_debit_transaction_informations: list[DirectDebitTransactionInformation9] = []
        for index, receipt in enumerate(receipts_by_iban):
            payment_identification = PaymentIdentification1()
            payment_identification.end_to_end_id = self.generate_receipt_id(index)
            direct_debit_transaction_information = self.create_direct_debit_transaction_information(
                payment_identification, receipt)
            direct_debit_transaction_informations.append(direct_debit_transaction_information)
        return direct_debit_transaction_informations

    def generate_receipt_id(self, receipt_index: int) -> str:
        return self.remittance.sepa_id + str(receipt_index+1) + datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def create_direct_debit_transaction_information(
            self, payment_identification: PaymentIdentification1,
            receipt: Receipt) -> DirectDebitTransactionInformation9:
        direct_debit_transaction_information = DirectDebitTransactionInformation9()
        direct_debit_transaction_information.pmt_id = payment_identification
        active_or_historic_currency_and_amount = ActiveOrHistoricCurrencyAndAmount()
        active_or_historic_currency_and_amount.ccy = self.EURO
        active_or_historic_currency_and_amount.value = format(receipt.amount, '.2f')
        direct_debit_transaction_information.instd_amt = active_or_historic_currency_and_amount
        direct_debit_transaction = DirectDebitTransaction6()
        mandate_related_information = MandateRelatedInformation6()
        mandate_related_information.mndt_id = receipt.authorization.number
        mandate_related_information.dt_of_sgntr = XmlDate.from_date(receipt.authorization.date)
        direct_debit_transaction.mndt_rltd_inf = mandate_related_information
        direct_debit_transaction_information.drct_dbt_tx = direct_debit_transaction
        branch_and_financial_institution_identification_deudor = BranchAndFinancialInstitutionIdentification4()
        financial_institution_identification_deudor = FinancialInstitutionIdentification7()
        generic_financial_identification = GenericFinancialIdentification1()
        generic_financial_identification.id = receipt.bic
        financial_institution_identification_deudor.othr = generic_financial_identification
        branch_and_financial_institution_identification_deudor.fin_instn_id = financial_institution_identification_deudor
        direct_debit_transaction_information.dbtr_agt = branch_and_financial_institution_identification_deudor
        party_identification_deudor = PartyIdentification32()
        party_identification_deudor.nm = receipt.bank_account_owner
        postal_address_deudor: PostalAddress6 = PostalAddress6()
        postal_address_deudor.ctry = self.COUNTRY
        party_identification_deudor.pstl_adr = postal_address_deudor
        party_identification_deudor.ctry_of_res = self.COUNTRY
        direct_debit_transaction_information.dbtr = party_identification_deudor
        cash_account_deudor = CashAccount16()
        account_identification_choice_deudor = AccountIdentification4Choice()
        account_identification_choice_deudor.iban = receipt.iban
        cash_account_deudor.id = account_identification_choice_deudor
        direct_debit_transaction_information.dbtr_acct = cash_account_deudor
        remittance_information = RemittanceInformation5()
        remittance_information.ustrd.append(self.remittance.concept)
        direct_debit_transaction_information.rmt_inf = remittance_information
        return direct_debit_transaction_information

    def create_party_identification_ctr_scheme(self) -> PartyIdentification32:
        party_identification = PartyIdentification32()
        generic_person_identification = GenericPersonIdentification1()
        generic_person_identification.id = self.generic_organisation_identification_id
        person_identification_scheme_name_choice = PersonIdentificationSchemeName1Choice()
        person_identification_scheme_name_choice.prtry = self.SEPA
        generic_person_identification.schme_nm = person_identification_scheme_name_choice
        person_identification = PersonIdentification5()
        person_identification.othr.append(generic_person_identification)
        party_choice = Party6Choice()
        party_choice.prvt_id = person_identification
        party_identification.id = party_choice
        return party_identification

    def create_branch_and_financial_institution_id(self) -> BranchAndFinancialInstitutionIdentification4:
        financial_institution_identification = FinancialInstitutionIdentification7()
        financial_institution_identification.bic = self.remittance.get_bic()
        branch_and_financial_institution_identification = BranchAndFinancialInstitutionIdentification4()
        branch_and_financial_institution_identification.fin_instn_id = financial_institution_identification
        return branch_and_financial_institution_identification

    def create_cash_account(self) -> CashAccount16:
        account_identification_choice = AccountIdentification4Choice()
        account_identification_choice.iban = self.remittance.get_iban()
        cash_account = CashAccount16()
        cash_account.id = account_identification_choice
        cash_account.ccy = self.EURO
        return cash_account

    def create_payment_date(self) -> XmlDate:
        return XmlDate.from_string(self.remittance.payment_date.strftime("%Y-%m-%d"))

    def create_party_identification_cdtr(self) -> PartyIdentification32:
        party_identification_32_payment_information = PartyIdentification32()
        party_identification_32_payment_information.nm = self.party_identification
        party_identification_32_payment_information.pstl_adr = PostalAddressCreator().create(self.COUNTRY)
        return party_identification_32_payment_information

    def create_payment_type_information(self) -> PaymentTypeInformation20:
        payment_type_information_20 = PaymentTypeInformation20()
        service_level_8_choice = ServiceLevel8Choice()
        service_level_8_choice.cd = self.SEPA
        payment_type_information_20.svc_lvl = service_level_8_choice
        local_instrument_2_choice = LocalInstrument2Choice()
        local_instrument_2_choice.cd = self.CORE
        payment_type_information_20.lcl_instrm = local_instrument_2_choice
        payment_type_information_20.seq_tp = SequenceType1Code.RCUR
        return payment_type_information_20
