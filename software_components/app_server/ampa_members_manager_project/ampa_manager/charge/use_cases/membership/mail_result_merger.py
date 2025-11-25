from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult


class MailResultMerger:

    @classmethod
    def merge(cls, results: list[MailNotifierResult]) -> MailNotifierResult:
        result = MailNotifierResult()
        for partial_result in results:
            result.append_success_emails(partial_result.success_emails)
            result.append_error_emails(partial_result.error_emails)
            if partial_result.error:
                if result.error is None:
                    result.error = partial_result.error
                else:
                    result.error += f'. {partial_result.error}'
        return result
