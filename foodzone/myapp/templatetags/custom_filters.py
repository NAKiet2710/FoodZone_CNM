from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def map_to_list(queryset, attr):
    """Lấy danh sách giá trị của một thuộc tính từ QuerySet"""
    result = []
    for item in queryset:
        # Hỗ trợ truy cập nested attribute như 'order.id'
        if '.' in attr:
            parts = attr.split('.')
            value = item
            for part in parts:
                value = getattr(value, part, None)
            result.append(value)
        else:
            result.append(getattr(item, attr, None))
    return result

@register.filter
def calculate_order_total(order_items, order_id):
    """Tính tổng tiền của đơn hàng từ danh sách OrderItem"""
    total = 0
    for item in order_items:
        if hasattr(item, 'order') and item.order.id == order_id:
            try:
                item_total = float(item.price) * float(item.quantity)
                total += item_total
            except (ValueError, TypeError):
                pass
    return total 