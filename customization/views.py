
from django.shortcuts import render, get_object_or_404, redirect
from .models import Dish
from .forms import DishForm

def dish_list(request):
    dishes = Dish.objects.all()
    return render(request, 'customization/dish_list.html', {'dishes': dishes})

def dish_detail(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    return render(request, 'customization/dish_detail.html', {'dish': dish})

def dish_create(request):
    if request.method == 'POST':
        form = DishForm(request.POST)
        if form.is_valid():
            model = form.save()
            return redirect('dish_detail', pk=model.pk)
    else:
        form = DishForm()
    return render(request, 'customization/dish_form.html', {'form': form})

def dish_edit(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == 'POST':
        form = DishForm(request.POST, instance=dish)
        if form.is_valid():
            dish = form.save()
            return redirect('model_detail', pk=dish.pk)
    else:
        form = DishForm(instance=dish)
    return render(request, 'customization/dish_form.html', {'form': form})

def dish_delete(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    dish.delete()
    return redirect('dish_list')
