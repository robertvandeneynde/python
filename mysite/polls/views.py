from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404

from django.core.urlresolvers import reverse

from polls.models import Choice, Poll

# def index(request):
    # latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    # template = loader.get_template('polls/index.html')
    # context = Context({
        # 'latest_poll_list': latest_poll_list,
    # })
    # return HttpResponse(template.render(context))
    # context = {'latest_poll_list': latest_poll_list}
    # return render(request, 'polls/index.html', context)
    
# def detail(request, poll_id):
    # try:
        # poll = Poll.objects.get(pk=poll_id)
    # except Poll.DoesNotExist:
        # raise Http404
    # return render(request, 'polls/detail.html', {'poll': poll})
    # poll = get_object_or_404(Poll, pk=poll_id)
    # return render(request, 'polls/detail.html', {'poll': poll})

# def results(request, poll_id):
    # poll = get_object_or_404(Poll, pk=poll_id)
    # return render(request, 'polls/results.html', {'poll': poll})

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))