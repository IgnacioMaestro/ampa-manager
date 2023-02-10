import codecs
import csv
import locale
from typing import List

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime, XmlDate

from ampa_manager.read_only_inline import ReadOnlyTabularInline
from ..models.activity_remittance import ActivityRemittance
from ..models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ..models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ..models.fee.fee import Fee
from ..models.membership_receipt import MembershipReceipt
from ..models.membership_remittance import MembershipRemittance
from ..remittance import Remittance
from ..sepa.xml_pain_008_001_02 import Document, CustomerDirectDebitInitiationV02, GroupHeader39, \
    PaymentInstructionInformation4, PartyIdentification32, Party6Choice, OrganisationIdentification4, \
    GenericOrganisationIdentification1, PaymentMethod2Code, PaymentTypeInformation20, ServiceLevel8Choice, \
    LocalInstrument2Choice, SequenceType1Code, PostalAddress6, CashAccount16, AccountIdentification4Choice, \
    BranchAndFinancialInstitutionIdentification4, FinancialInstitutionIdentification7, PersonIdentification5, \
    GenericPersonIdentification1, PersonIdentificationSchemeName1Choice, DirectDebitTransactionInformation9, \
    PaymentIdentification1, ActiveOrHistoricCurrencyAndAmount, DirectDebitTransaction6, MandateRelatedInformation6, \
    GenericFinancialIdentification1, RemittanceInformation5
from ..state import State
from ..use_cases.activity.generate_remittance_from_activity_remittance.remittance_generator import RemittanceGenerator
from ..use_cases.after_school.remittance_generator_from_after_school_remittance import RemittanceGeneratorFromAfterSchoolRemittance
from ..use_cases.membership.create_membership_remittance_for_unique_families.membership_remittance_creator_of_active_course import \
    MembershipRemittanceCreatorOfActiveCourse
from ..use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator
from ..models.activity_receipt import ActivityReceipt

TEXT_CSV = 'text/csv'
TEXT_XML = 'text/xml'
SEPA = 'SEPA'
CORE = 'CORE'
EURO = 'EUR'
PAIS = 'ES'
RECEIPTS_SET_AS_SENT_MESSAGE = "%(num_receipts)s receipts set as sent"
RECEIPTS_SET_AS_PAID_MESSAGE = "%(num_receipts)s receipts set as paid"


class ActivityReceiptInline(ReadOnlyTabularInline):
    model = ActivityReceipt
    extra = 0


class ActivityReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'amount', 'state', 'activity_registrations_count', 'family', 'children', 'activities']
    ordering = ['remittance', 'state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.display(description=gettext_lazy('Family'))
    def family(self, activity_receipt):
        families = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if activity_registration.child.family.surnames not in families:
                families.append(activity_registration.child.family.surnames)
        return ', '.join(families)

    @admin.display(description=gettext_lazy('Children'))
    def children(self, activity_receipt):
        children_list = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if activity_registration.child.name not in children_list:
                children_list.append(activity_registration.child.name)
        return ', '.join(children_list)

    @admin.display(description=gettext_lazy('Activities'))
    def activities(self, activity_receipt):
        activities_list = []
        for activity_registration in activity_receipt.activity_registrations.all():
            if str(activity_registration.activity_period) not in activities_list:
                activities_list.append(str(activity_registration.activity_period))
        return ', '.join(activities_list)

    @admin.display(description=gettext_lazy('Activities'))
    def activity_registrations_count(self, activity_receipt):
        return activity_receipt.activity_registrations.count()

    list_filter = ['state', 'remittance__name']
    actions = [set_as_sent, set_as_paid]


class ActivityRemittanceAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'name', 'receipt_count', 'receipt_created_count', 'receipt_sent_count',
                    'receipt_paid_count']
    ordering = ['-created_at']
    list_filter = ['created_at']
    inlines = [ActivityReceiptInline]
    list_per_page = 25

    @admin.action(description=gettext_lazy("Export to CSV"))
    def download_csv(self, request, queryset: QuerySet[ActivityRemittance]):
        if queryset.count() > 1:
            return self.message_user(
                request=request,
                message=gettext_lazy("Only one activity remittance can be selected at a time"))
        remittance: Remittance = RemittanceGenerator(activity_remittance=queryset.first()).generate()
        return ActivityRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Set all receipts as sent"))
    def set_all_receipts_as_sent(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.SEND)

            message_vars = {'num_receipts': remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = gettext_lazy("%(num_receipts)s receipts set as sent for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set all receipts as paid"))
    def set_all_receipts_as_paid(self, request, queryset: QuerySet[ActivityRemittance]):
        for remittance in queryset:
            remittance.activityreceipt_set.update(state=State.PAID)

            message_vars = {'num_receipts': remittance.activityreceipt_set.count(), 'remittance': str(remittance)}
            message = gettext_lazy("%(num_receipts)s receipts set as paid for remittance %(remittance)s") % message_vars
            self.message_user(request=request, message=message)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response, quoting=csv.QUOTE_ALL).writerows(remittance.obtain_rows())
        return response

    @admin.display(description=gettext_lazy('Total receipts'))
    def receipt_count(self, remittance):
        return remittance.activityreceipt_set.count()

    @admin.display(description=gettext_lazy('Created receipts'))
    def receipt_created_count(self, remittance):
        return remittance.get_receipt_count(state=State.CREATED)

    @admin.display(description=gettext_lazy('Sent receipts'))
    def receipt_sent_count(self, remittance):
        return remittance.get_receipt_count(state=State.SEND)

    @admin.display(description=gettext_lazy('Paid receipts'))
    def receipt_paid_count(self, remittance):
        return remittance.get_receipt_count(state=State.PAID)

    actions = [download_csv, set_all_receipts_as_sent, set_all_receipts_as_paid]


class MembershipReceiptInline(ReadOnlyTabularInline):
    model = MembershipReceipt
    extra = 0


class MembershipRemittanceAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'created_at', 'course', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    inlines = [MembershipReceiptInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        number_of_receipts = MembershipReceipt.objects.of_remittance(remittance).count()
        fee = Fee.objects.filter(academic_course=remittance.course).first()
        if fee:
            total = number_of_receipts * fee.amount
            locale.setlocale(locale.LC_ALL, 'es_ES')
            return locale.format_string('%d €', total, grouping=True)
        return '0 €'

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return MembershipReceipt.objects.of_remittance(remittance).count()

    @admin.action(description=gettext_lazy("Export Membership Remittance to CSV"))
    def download_membership_remittance_csv(self, request, queryset: QuerySet[MembershipRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy("Only can select one membership remittance"))
        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance=queryset.first()).generate()
        return MembershipRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Create Membership Remittance with families not included yet"))
    def create_remittance(self, request, _: QuerySet[MembershipRemittance]):
        membership_remittance: MembershipRemittance = MembershipRemittanceCreatorOfActiveCourse.create()
        if membership_remittance:
            message = mark_safe(
                gettext_lazy(
                    "Membership remittance created") + " (<a href=\"" + membership_remittance.get_admin_url() + "\">" + gettext_lazy(
                    "View details") + "</a>)")
            return self.message_user(request=request, message=message)
        else:
            message = gettext_lazy("No families to include in Membership Remittance")
            return self.message_user(request=request, message=message)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        csv.writer(response).writerows(remittance.obtain_rows())
        return response

    actions = [download_membership_remittance_csv, create_remittance]


class MembershipReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'family', 'state']
    ordering = ['state']
    search_fields = ['family__surnames']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[ActivityReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]


class AfterSchoolReceiptAdmin(admin.ModelAdmin):
    list_display = ['remittance', 'after_school_registration', 'state', 'amount']
    ordering = ['state']
    search_fields = ['after_school_registration__child__family']
    list_filter = ['state']
    list_per_page = 25

    @admin.action(description=gettext_lazy("Set as sent"))
    def set_as_sent(self, request, queryset: QuerySet[AfterSchoolReceipt]):
        queryset.update(state=State.SEND)

        message = gettext_lazy(RECEIPTS_SET_AS_SENT_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    @admin.action(description=gettext_lazy("Set as paid"))
    def set_as_paid(self, request, queryset: QuerySet[AfterSchoolReceipt]):
        queryset.update(state=State.PAID)

        message = gettext_lazy(RECEIPTS_SET_AS_PAID_MESSAGE) % {'num_receipts': queryset.count()}
        self.message_user(request=request, message=message)

    actions = [set_as_sent, set_as_paid]


class AfterSchoolReceiptInline(ReadOnlyTabularInline):
    model = AfterSchoolReceipt
    extra = 0


class AfterSchoolRemittanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'receipts_total', 'receipts_count']
    ordering = ['-created_at']
    inlines = [AfterSchoolReceiptInline]
    list_per_page = 25

    @admin.display(description=gettext_lazy('Total'))
    def receipts_total(self, remittance):
        receipts = AfterSchoolReceipt.objects.filter(remittance=remittance)
        total = 0.0
        for receipt in receipts:
            total += receipt.amount
        locale.setlocale(locale.LC_ALL, 'es_ES')
        return locale.format_string('%d €', total, grouping=True)

    @admin.display(description=gettext_lazy('Receipts'))
    def receipts_count(self, remittance):
        return AfterSchoolReceipt.objects.filter(remittance=remittance).count()

    @admin.action(description=gettext_lazy("Export after-school remittance to CSV"))
    def download_membership_remittance_csv(self, request, queryset: QuerySet[AfterSchoolRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy("Only can select one membership remittance"))
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=queryset.first()).generate()
        return AfterSchoolRemittanceAdmin.create_csv_response_from_remittance(remittance)

    @admin.action(description=gettext_lazy("Export after-school remittance to SEPA file"))
    def download_membership_remittance_sepa_file(self, request, queryset: QuerySet[AfterSchoolRemittance]):
        if queryset.count() > 1:
            return self.message_user(request=request, message=gettext_lazy("Only can select one membership remittance"))
        remittance: Remittance = RemittanceGeneratorFromAfterSchoolRemittance(
            after_school_remittance=queryset.first()).generate()
        return AfterSchoolRemittanceAdmin.create_sepa_response_from_remittance(remittance)

    @staticmethod
    def create_csv_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.csv"'}
        response = HttpResponse(content_type=TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        rows_to_add: List[List[str]] = [['Titular', 'BIC', 'IBAN', 'Autorizacion', 'Fecha Autorizacion', 'Cantidad']]
        rows_to_add.extend(remittance.obtain_rows())
        csv.writer(response).writerows(rows_to_add)
        return response

    @staticmethod
    def create_sepa_response_from_remittance(remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.xml"'}
        response = HttpResponse(content_type=TEXT_XML, headers=headers)
        response.write(codecs.BOM_UTF8)
        # TODO: Sacar a funcion o usar Stream.
        suma: float = 0
        for receipt in remittance.receipts:
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

        groupheader39.msg_id = "Nombre Remesa"
        # Fecha cuando se crea la remesa
        now_str: str = remittance.created_date.strftime("%Y-%m-%dT%H:%M:%S")
        creation_date: XmlDateTime = XmlDateTime.from_string(now_str)
        groupheader39.cre_dt_tm = creation_date
        groupheader39.nb_of_txs = len(remittance.obtain_rows())
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
        for receipt in remittance.receipts:
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

    actions = [download_membership_remittance_csv, download_membership_remittance_sepa_file]
