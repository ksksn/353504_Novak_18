from django.core.management.base import BaseCommand
from main.models import Repair, Contract, Order

class Command(BaseCommand):
    help = 'Пересчитывает все стоимости в системе'

    def handle(self, *args, **options):
        self.stdout.write('Пересчет стоимости ремонтов...')
        
        # Пересчитываем стоимость всех ремонтов
        repairs_count = 0
        for repair in Repair.objects.all():
            repair.calculate_total_cost()
            repair.save(update_fields=['total_cost'])
            repairs_count += 1
        
        self.stdout.write(f'Обновлено ремонтов: {repairs_count}')
        
        # Пересчитываем стоимость всех заказов
        orders_count = 0
        for order in Order.objects.all():
            order.calculate_sums()
            order.save(update_fields=['service_sum', 'parts_sum', 'total_sum'])
            orders_count += 1
        
        self.stdout.write(f'Обновлено заказов: {orders_count}')
        
        # Пересчитываем стоимость всех договоров
        contracts_count = 0
        for contract in Contract.objects.all():
            contract.calculate_total_sum()
            contracts_count += 1
        
        self.stdout.write(f'Обновлено договоров: {contracts_count}')
        
        self.stdout.write(
            self.style.SUCCESS('Все стоимости успешно пересчитаны!')
        )
