import codecs

from django.http import HttpResponse

from ..receipt import Receipt
from ..sepa.xml_pain_008_001_02 import Document, CustomerDirectDebitInitiationV02, GroupHeader39, \
    PaymentInstructionInformation4, PartyIdentification32, Party6Choice, OrganisationIdentification4, \
    GenericOrganisationIdentification1, PaymentMethod2Code, PaymentTypeInformation20, ServiceLevel8Choice, \
    LocalInstrument2Choice, SequenceType1Code, PostalAddress6, CashAccount16, AccountIdentification4Choice, \
    BranchAndFinancialInstitutionIdentification4, FinancialInstitutionIdentification7, PersonIdentification5, \
    GenericPersonIdentification1, PersonIdentificationSchemeName1Choice, DirectDebitTransactionInformation9, \
    PaymentIdentification1, ActiveOrHistoricCurrencyAndAmount, DirectDebitTransaction6, MandateRelatedInformation6, \
    GenericFinancialIdentification1, RemittanceInformation5
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime, XmlDate

from ..admin import TEXT_XML, SEPA, CORE, PAIS, EURO
from ampa_manager.charge.remittance import Remittance


class SEPAResponseCreator:
    def create(self, remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.xml"'}
        response = HttpResponse(content_type=TEXT_XML, headers=headers)
        response.write(codecs.BOM_UTF8)
        receipts_by_iban: list[Receipt] = self.group_receipts_by_iban(remittance.receipts)
        suma: float = 0
        for receipt in receipts_by_iban:
            suma = suma + receipt.amount
        suma = float(format(suma, '.2f'))
        print("Empiezo a rellenar")
        document: Document = Document()
        customerdirectdebitinitiationv02: CustomerDirectDebitInitiationV02 = CustomerDirectDebitInitiationV02()
        document.cstmr_drct_dbt_initn = customerdirectdebitinitiationv02
        groupheader39: GroupHeader39 = GroupHeader39()
        customerdirectdebitinitiationv02.grp_hdr = groupheader39
        paymentinstructioninformation4: PaymentInstructionInformation4 = PaymentInstructionInformation4()
        customerdirectdebitinitiationv02.pmt_inf.append(paymentinstructioninformation4)

        groupheader39.msg_id = remittance.name
        # Fecha cuando se crea la remesa
        now_str: str = remittance.created_date.strftime("%Y-%m-%dT%H:%M:%S")
        creation_date: XmlDateTime = XmlDateTime.from_string(now_str)
        groupheader39.cre_dt_tm = creation_date
        groupheader39.nb_of_txs = len(receipts_by_iban)
        groupheader39.ctrl_sum = suma

        partyidentification32cabecera: PartyIdentification32 = PartyIdentification32()
        partyidentification32cabecera.nm = "AMPA IKASTOLA ABENDANO"
        party6choice_cabecera: Party6Choice = Party6Choice()
        organisationidentification4: OrganisationIdentification4 = OrganisationIdentification4()
        genericorganisationidentification1: GenericOrganisationIdentification1 = GenericOrganisationIdentification1()
        genericorganisationidentification1.id = "ES28000G01025451"
        organisationidentification4.othr.append(genericorganisationidentification1)
        party6choice_cabecera.org_id = organisationidentification4
        partyidentification32cabecera.id = party6choice_cabecera
        groupheader39.initg_pty = partyidentification32cabecera

        # TODO: Aqui se pone un identificador de la remesa. Por ejemplo año/numero de remesa
        paymentinstructioninformation4.pmt_inf_id = "2023/001"
        paymentinstructioninformation4.pmt_mtd = PaymentMethod2Code.DD
        paymentinstructioninformation4.nb_of_txs = len(remittance.obtain_rows())
        paymentinstructioninformation4.ctrl_sum = suma
        paymentinstructioninformation4.btch_bookg = True

        paymenttypeinformation20: PaymentTypeInformation20 = PaymentTypeInformation20()
        servicelevel8choice: ServiceLevel8Choice = ServiceLevel8Choice()
        servicelevel8choice.cd = SEPA
        paymenttypeinformation20.svc_lvl = servicelevel8choice
        localinstrument2choice: LocalInstrument2Choice = LocalInstrument2Choice()
        localinstrument2choice.cd = CORE
        paymenttypeinformation20.lcl_instrm = localinstrument2choice
        paymenttypeinformation20.seq_tp = SequenceType1Code.RCUR
        paymentinstructioninformation4.pmt_tp_inf = paymenttypeinformation20
        # TODO: Fecha cuando se va a cobrar la remesa. Formato YYYY-MM-DD
        paymentinstructioninformation4.reqd_colltn_dt = XmlDateTime.now()

        partyidentification32informacionpago: PartyIdentification32 = PartyIdentification32()
        partyidentification32informacionpago.nm = "AMPA IKASTOLA ABENDANO"
        postaladdress6: PostalAddress6 = PostalAddress6()
        postaladdress6.pst_cd = "01008"
        postaladdress6.twn_nm = "VITORIA-GASTEIZ"
        postaladdress6.ctry = PAIS
        postaladdress6.adr_line = "Mexico Kalea, 9"
        partyidentification32informacionpago.pstl_adr = postaladdress6
        paymentinstructioninformation4.cdtr = partyidentification32informacionpago

        cashaccount16: CashAccount16 = CashAccount16()
        accountidentification4choice: AccountIdentification4Choice = AccountIdentification4Choice()
        # TODO: Modificar para que se pueda elegir entre las cuentas que tiene el AMPA
        accountidentification4choice.iban = "ES2430350061920611157807"
        cashaccount16.id = accountidentification4choice
        cashaccount16.ccy = EURO
        paymentinstructioninformation4.cdtr_acct = cashaccount16

        branchandfinancialinstitutionidentification4: BranchAndFinancialInstitutionIdentification4 = \
            BranchAndFinancialInstitutionIdentification4()
        financialinstitutionidentification7: FinancialInstitutionIdentification7 = FinancialInstitutionIdentification7()
        financialinstitutionidentification7.bic = "CLPEES2MXXX"
        branchandfinancialinstitutionidentification4.fin_instn_id = financialinstitutionidentification7
        paymentinstructioninformation4.cdtr_agt = branchandfinancialinstitutionidentification4

        partyidentification32: PartyIdentification32 = PartyIdentification32()
        party6choice: Party6Choice = Party6Choice()
        personidentification5: PersonIdentification5 = PersonIdentification5()
        genericpersonidentification1: GenericPersonIdentification1 = GenericPersonIdentification1()
        genericpersonidentification1.id = "ES28000G01025451"
        personidentificationschemename1choice: PersonIdentificationSchemeName1Choice = \
            PersonIdentificationSchemeName1Choice()
        personidentificationschemename1choice.prtry = SEPA
        genericpersonidentification1.schme_nm = personidentificationschemename1choice
        personidentification5.othr.append(genericpersonidentification1)
        party6choice.prvt_id = personidentification5
        partyidentification32.id = party6choice
        paymentinstructioninformation4.cdtr_schme_id = partyidentification32

        # El pais es el mismo para todos los deudores.
        postaladdress6deudor: PostalAddress6 = PostalAddress6()
        postaladdress6deudor.ctry = PAIS
        paymentidentification1: PaymentIdentification1 = PaymentIdentification1()
        # TODO: Esto tiene que ser variable. El sistema genera una clave exclusiva para cada pago, formada por
        #  la cuenta bancaria, el proveedor, la fecha del pago y el número de control del cheque.
        paymentidentification1.end_to_end_id = "2022/Socio"
        # Definimos varables que se usan dentro del bucle
        directdebittransactioninformation9: DirectDebitTransactionInformation9
        activeorhistoriccurrencyandamount: ActiveOrHistoricCurrencyAndAmount
        directdebittransaction6: DirectDebitTransaction6
        mandaterelatedinformation6: MandateRelatedInformation6
        branchandfinancialinstitutionidentification4deudor: BranchAndFinancialInstitutionIdentification4
        financialinstitutionidentification7deudor: FinancialInstitutionIdentification7
        genericfinancialidentification1: GenericFinancialIdentification1
        partyidentification32deudor: PartyIdentification32
        cashaccount16deudor: CashAccount16
        accountidentification4choicedeudor: AccountIdentification4Choice
        remittanceinformation5: RemittanceInformation5
        # Empieza el bucle por cada uno de los recibos
        for receipt in receipts_by_iban:
            directdebittransactioninformation9 = DirectDebitTransactionInformation9()
            directdebittransactioninformation9.pmt_id = paymentidentification1
            activeorhistoriccurrencyandamount = ActiveOrHistoricCurrencyAndAmount()
            activeorhistoriccurrencyandamount.ccy = EURO
            activeorhistoriccurrencyandamount.value = format(receipt.amount, '.2f')
            directdebittransactioninformation9.instd_amt = activeorhistoriccurrencyandamount
            directdebittransaction6 = DirectDebitTransaction6()
            mandaterelatedinformation6 = MandateRelatedInformation6()
            mandaterelatedinformation6.mndt_id = receipt.authorization.number
            #TODO: Si no hay fecha de autorización da una Excepción.
            mandaterelatedinformation6.dt_of_sgntr = XmlDate.from_date(receipt.authorization.date)
            directdebittransaction6.mndt_rltd_inf = mandaterelatedinformation6
            directdebittransactioninformation9.drct_dbt_tx = directdebittransaction6
            branchandfinancialinstitutionidentification4deudor = BranchAndFinancialInstitutionIdentification4()
            financialinstitutionidentification7Deudor = FinancialInstitutionIdentification7()
            genericfinancialidentification1 = GenericFinancialIdentification1()
            genericfinancialidentification1.id = receipt.bic
            financialinstitutionidentification7Deudor.othr = genericfinancialidentification1
            branchandfinancialinstitutionidentification4deudor.fin_instn_id = financialinstitutionidentification7Deudor
            directdebittransactioninformation9.dbtr_agt = branchandfinancialinstitutionidentification4deudor
            partyidentification32deudor = PartyIdentification32()
            partyidentification32deudor.nm = receipt.bank_account_owner
            partyidentification32deudor.pstl_adr = postaladdress6deudor
            partyidentification32deudor.ctry_of_res = PAIS
            directdebittransactioninformation9.dbtr = partyidentification32deudor
            cashaccount16deudor = CashAccount16()
            accountidentification4choicedeudor = AccountIdentification4Choice()
            accountidentification4choicedeudor.iban = receipt.iban
            cashaccount16deudor.id = accountidentification4choicedeudor
            directdebittransactioninformation9.dbtr_acct = cashaccount16deudor
            remittanceinformation5 = RemittanceInformation5()
            #TODO: Poner concepto del recibo variable
            remittanceinformation5.ustrd.append("Cuota socio 2022/23")
            directdebittransactioninformation9.rmt_inf = remittanceinformation5
            paymentinstructioninformation4.drct_dbt_tx_inf.append(directdebittransactioninformation9)
            #Fin de bucle
        # Escribo el fichero al response
        print("Empiezo a serializar")
        config = SerializerConfig(pretty_print=True)
        serializer = XmlSerializer(config)
        xml = serializer.render(document, ns_map={None: "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"})
        response.write(xml)

        return response

    def group_receipts_by_iban(self, receipts: list[Receipt]) -> list[Receipt]:
        grouped_receipts = {}
        for receipt in receipts:
            if receipt.iban in grouped_receipts:
                grouped_receipts[receipt.iban].amount += receipt.amount
            else:
                grouped_receipts[receipt.iban] = Receipt(amount=receipt.amount,
                                                         bank_account_owner=receipt.bank_account_owner,
                                                         iban=receipt.iban,
                                                         bic=receipt.bic,
                                                         authorization=receipt.authorization)
        return list(grouped_receipts.values())
