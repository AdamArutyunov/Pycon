from .Permissions import *


class Role:
    id = 0
    permissions = 0
    display_name = "Абстрактная роль"
    color = "#FFFFFF"

    @staticmethod
    def is_permitted(permission):
        return Role.permissions & permission == permission


class BannedRole(Role):
    id = -1
    permissions = 0
    display_name = "Забаненный"
    color = "#DD0000"

    @staticmethod
    def is_permitted(permission):
        return False


class ObserverRole(Role):
    id = 1
    permissions = (Permissions.INDEX_VIEW | Permissions.PROBLEMS_VIEW | Permissions.PROBLEM_VIEW |
                   Permissions.CONTESTS_VIEW | Permissions.CONTEST_VIEW | Permissions.CONTEST_VIEW_STANDINGS)

    @staticmethod
    def is_permitted(permission):
        return ObserverRole.permissions & permission == permission


class UserRole(Role):
    id = 2
    permissions = (ObserverRole.permissions | Permissions.PROBLEM_SUBMIT | Permissions.PROBLEM_VIEW_SUBMISSIONS |
                   Permissions.SUBMISSIONS_VIEW | Permissions.SUBMISSION_VIEW | Permissions.CONTEST_JOIN |
                   Permissions.NEWS_RATE | Permissions.NEWS_UNRATE | Permissions.FEEDBACK_LEAVE)
    display_name = "Пользователь"
    color = "#000000"

    @staticmethod
    def is_permitted(permission):
        return UserRole.permissions & permission == permission


class GroupLeaderRole(Role):
    id = 3
    permissions = (UserRole.permissions | Permissions.GROUP_VIEW |
                   Permissions.GROUP_ADD_USER | Permissions.GROUP_REMOVE_USER)

    display_name = "Староста"
    color = "#FFA500"

    @staticmethod
    def is_permitted(permission):
        return GroupLeaderRole.permissions & permission == permission


class TeacherRole(Role):
    id = 4
    permissions = (GroupLeaderRole.permissions | Permissions.PROBLEM_CREATE | Permissions.PROBLEM_EDIT |
                   Permissions.PROBLEM_DELETE | Permissions.PROBLEM_VIEW_TESTS | Permissions.PROBLEM_CREATE_TEST |
                   Permissions.PROBLEM_EDIT_TEST | Permissions.PROBLEM_DELETE_TEST | Permissions.SUBMISSIONS_VIEW_ALL |
                   Permissions.CONTEST_CREATE | Permissions.CONTEST_EDIT | Permissions.CONTEST_DELETE |
                   Permissions.CONTEST_ADD_PROBLEM | Permissions.CONTEST_REMOVE_PROBLEM |
                   Permissions.CONTEST_DOWNLOAD_STANDINGS | Permissions.GROUPS_VIEW | Permissions.GROUP_CREATE |
                   Permissions.GROUP_EDIT | Permissions.GROUP_DELETE)
    display_name = "Преподаватель"
    color = "0000C2"

    @staticmethod
    def is_permitted(permission):
        return TeacherRole.permissions & permission == permission


class AdminRole(Role):
    id = 5
    permissions = (TeacherRole.permissions | Permissions.NEWS_CREATE | Permissions.NEWS_EDIT | Permissions.NEWS_DELETE |
                   Permissions.ASSIGN_ROLES)
    display_name = "Администратор"
    color = "#660099"

    @staticmethod
    def is_permitted(permission):
        return AdminRole.permissions & permission == permission


ROLES = [Role, ObserverRole, UserRole, GroupLeaderRole, TeacherRole, AdminRole, BannedRole]
