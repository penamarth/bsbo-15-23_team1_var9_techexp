from abc import ABC, abstractmethod

# ============================================================
#                         USERS
# ============================================================

class User:
    def __init__(self, user_id: int, name: str, email: str, role: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role

    def login(self):
        print(f"[Login] {self.name} logged in as {self.role}")

    def logout(self):
        print(f"[Logout] {self.name} logged out")

    def update_profile(self, profile_data: dict):
        print(f"[Profile Update] {self.name}: {profile_data}")


class Applicant:
    def __init__(self, user: User):
        self.user = user


class Expert:
    def __init__(self, user: User, specialization: str):
        self.user = user
        self.specialization = specialization


class FundHolder:
    def __init__(self, user: User, note: str):
        self.user = user
        self.note = note


# ============================================================
#                         STATE PATTERN
# ============================================================

class ApplicationState(ABC):
    @abstractmethod
    def submit(self, app): pass

    @abstractmethod
    def review(self, app): pass

    @abstractmethod
    def evaluate(self, app): pass

    @abstractmethod
    def withdraw(self, app): pass

    @abstractmethod
    def decide(self, app, decision): pass


class SubmittedState(ApplicationState):
    def submit(self, app):
        print("[SubmittedState] Already submitted")

    def review(self, app):
        print("[SubmittedState] Moving to UNDER_REVIEW")
        app.set_state(UnderReviewState())

    def evaluate(self, app):
        print("[SubmittedState] Cannot evaluate, not under review")

    def withdraw(self, app):
        print("[SubmittedState] Withdrawing application")
        app.set_state(WithdrawnState())

    def decide(self, app, decision):
        print("[SubmittedState] Cannot decide, not evaluated")


class UnderReviewState(ApplicationState):
    def submit(self, app):
        print("[UnderReviewState] Already submitted")

    def review(self, app):
        print("[UnderReviewState] Already under review")

    def evaluate(self, app):
        print("[UnderReviewState] Evaluating application")
        app.set_state(EvaluatedState())

    def withdraw(self, app):
        print("[UnderReviewState] Withdrawing application")
        app.set_state(WithdrawnState())

    def decide(self, app, decision):
        print("[UnderReviewState] Cannot decide, not evaluated")


class EvaluatedState(ApplicationState):
    def submit(self, app):
        print("[EvaluatedState] Already submitted")

    def review(self, app):
        print("[EvaluatedState] Already reviewed")

    def evaluate(self, app):
        print("[EvaluatedState] Already evaluated")

    def withdraw(self, app):
        print("[EvaluatedState] Cannot withdraw, already evaluated")

    def decide(self, app, decision):
        print(f"[EvaluatedState] Decision applied: {decision}")
        if decision == "APPROVED":
            app.set_state(ApprovedState())
        else:
            app.set_state(RejectedState())


class WithdrawnState(ApplicationState):
    def submit(self, app):
        print("[WithdrawnState] Cannot submit, withdrawn")

    def review(self, app):
        print("[WithdrawnState] Cannot review, withdrawn")

    def evaluate(self, app):
        print("[WithdrawnState] Cannot evaluate, withdrawn")

    def withdraw(self, app):
        print("[WithdrawnState] Already withdrawn")

    def decide(self, app, decision):
        print("[WithdrawnState] Cannot decide, withdrawn")


class ApprovedState(ApplicationState):
    def submit(self, app): pass
    def review(self, app): pass
    def evaluate(self, app): pass
    def withdraw(self, app): pass
    def decide(self, app, decision): pass


class RejectedState(ApplicationState):
    def submit(self, app): pass
    def review(self, app): pass
    def evaluate(self, app): pass
    def withdraw(self, app): pass
    def decide(self, app, decision): pass


# ============================================================
#                         APPLICATION
# ============================================================

class Application:
    def __init__(self, application_id, title, description, applicant_id):
        self.application_id = application_id
        self.title = title
        self.description = description
        self.applicant_id = applicant_id
        self.state: ApplicationState = SubmittedState()

    def get_state(self):
        return type(self.state).__name__

    def set_state(self, state: ApplicationState):
        self.state = state

    def submit(self):
        self.state.submit(self)

    def start_review(self):
        self.state.review(self)

    def evaluate(self):
        self.state.evaluate(self)

    def withdraw(self):
        self.state.withdraw(self)

    def make_decision(self, decision):
        self.state.decide(self, decision)


# ============================================================
#                         SERVICES
# ============================================================

class ApplicationService:
    def __init__(self):
        self.applications = {}
        self.next_id = 1

    def create_application(self, title, description, applicant_id):
        app_id = self.next_id
        self.next_id += 1
        app = Application(app_id, title, description, applicant_id)
        self.applications[app_id] = app
        print(f"[ApplicationService] Created application {app_id}")
        return app

    def get_applications_by_applicant(self, applicant_id):
        return [app for app in self.applications.values() if app.applicant_id == applicant_id]


class Evaluation:
    def __init__(self, evaluation_id, application_id, expert_id, score, comments):
        self.evaluation_id = evaluation_id
        self.application_id = application_id
        self.expert_id = expert_id
        self.score = score
        self.comments = comments

    def is_valid(self):
        return 0 <= self.score <= 100 and bool(self.comments)


class EvaluationService:
    def __init__(self):
        self.evaluations = {}
        self.next_id = 1

    def save_evaluation(self, application: Application, expert_id, score, comments):
        if type(application.state).__name__ != "UnderReviewState":
            print("[EvaluationService] Cannot evaluate, application not under review")
            return None
        eval_id = self.next_id
        self.next_id += 1
        evaluation = Evaluation(eval_id, application.application_id, expert_id, score, comments)
        self.evaluations[eval_id] = evaluation
        application.evaluate()  # State change to Evaluated
        print(f"[EvaluationService] Saved evaluation {eval_id}")
        return evaluation


class Decision:
    def __init__(self, decision_id, application_id, fund_holder_id, status, notes):
        self.decision_id = decision_id
        self.application_id = application_id
        self.fund_holder_id = fund_holder_id
        self.status = status
        self.notes = notes

    def approve(self):
        self.status = "APPROVED"

    def reject(self):
        self.status = "REJECTED"


class DecisionService:
    def __init__(self):
        self.decisions = {}
        self.next_id = 1

    def assign_experts(self, application: Application, expert_ids):
        print(f"[DecisionService] Assigned experts {expert_ids} to application {application.application_id}")

    def save_decision(self, application: Application, fund_holder_id, status, notes):
        decision_id = self.next_id
        self.next_id += 1
        decision = Decision(decision_id, application.application_id, fund_holder_id, status, notes)
        if status == "APPROVED":
            application.make_decision("APPROVED")
        else:
            application.make_decision("REJECTED")
        self.decisions[decision_id] = decision
        print(f"[DecisionService] Saved decision {decision_id} with status {status}")


# ============================================================
#                         FACADE
# ============================================================

class SystemFacade:
    def __init__(self):
        self.application_service = ApplicationService()
        self.evaluation_service = EvaluationService()
        self.decision_service = DecisionService()

    # Applicants
    def submit_application(self, applicant_id, title, description):
        app = self.application_service.create_application(title, description, applicant_id)
        app.submit()
        return app

    def view_status(self, applicant_id):
        apps = self.application_service.get_applications_by_applicant(applicant_id)
        for app in apps:
            print(f"[Status] Application {app.application_id}: {app.get_state()}")

    def withdraw_application(self, applicant_id, application_id):
        app = self.application_service.applications.get(application_id)
        if app and app.applicant_id == applicant_id:
            app.withdraw()
        else:
            print("[Facade] Application not found or access denied")

    # Experts
    def evaluate_application(self, expert_id, application_id, score, comments):
        app = self.application_service.applications.get(application_id)
        self.evaluation_service.save_evaluation(app, expert_id, score, comments)

    # FundHolder
    def assign_experts(self, fund_holder_id, application_id, expert_ids):
        app = self.application_service.applications.get(application_id)
        self.decision_service.assign_experts(app, expert_ids)

    def make_decision(self, fund_holder_id, application_id, status, notes):
        app = self.application_service.applications.get(application_id)
        self.decision_service.save_decision(app, fund_holder_id, status, notes)


# ============================================================
#                         TEST
# ============================================================

if __name__ == "__main__":
    facade = SystemFacade()

    # Создаем пользователей
    applicant = Applicant(User(1, "Alice", "alice@mail.com", "Applicant"))
    expert = Expert(User(2, "Bob", "bob@mail.com", "Expert"), "Physics")
    fund_holder = FundHolder(User(3, "Charlie", "charlie@mail.com", "FundHolder"), "Manager")

    # Подача заявки
    app1 = facade.submit_application(applicant.user.user_id, "Project X", "Description X")

    # Просмотр статуса
    facade.view_status(applicant.user.user_id)

    # Назначение эксперта и оценка
    facade.assign_experts(fund_holder.user.user_id, app1.application_id, [expert.user.user_id])
    facade.evaluate_application(expert.user.user_id, app1.application_id, 85, "Good work")

    # Просмотр статуса после оценки
    facade.view_status(applicant.user.user_id)

    # Принятие решения
    facade.make_decision(fund_holder.user.user_id, app1.application_id, "APPROVED", "Excellent")
    facade.view_status(applicant.user.user_id)
