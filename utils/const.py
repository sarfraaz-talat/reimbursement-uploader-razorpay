from enum import Enum

class Category(Enum):
    TRAVEL = '1'
    TELEPHONE = '5'
    INTERNET = '10257'
    HEALTH = '10256'
    UNKNOWN = '-1'

budgets = {
    Category.TRAVEL: 4000,
    Category.TELEPHONE: 1100,
    Category.INTERNET: 1100,
    Category.HEALTH: 2000,
}

reasons = {
    Category.TRAVEL: 'cab to/from office',
    Category.TELEPHONE: 'Mobile recharge',
    Category.INTERNET: 'Internet',
    Category.HEALTH: 'Health/Wellness',
}