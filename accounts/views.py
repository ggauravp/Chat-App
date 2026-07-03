from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from chat.models import Conversation
from friends.models import FriendRequest
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/signup.html", {"error": "User already exists"})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        conversation = Conversation.objects.create()
        return redirect("login")

    return render(request, "accounts/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile")
        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")

@login_required(login_url="login")
def profile_view(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user).order_by("-created_at")

    friends = []
    friend_ids = set()
    for conversation in conversations:
        partner = conversation.participants.exclude(id=user.id).first()
        if partner and partner.id not in friend_ids:
            friend_ids.add(partner.id)
            friends.append({
                "user": partner,
                "conversation": conversation,
            })

    discover_users = []
    all_users = User.objects.exclude(id=user.id).exclude(id__in=friend_ids)
    for other_user in all_users:
        existing_conversation = conversations.filter(participants=other_user).first()
        discover_users.append({
            "user": other_user,
            "conversation": existing_conversation,
        })

    context = {
        "user": user,
        "friends": friends,
        "discover_users": discover_users,
    }
    # pending requests count for navbar badge
    pending_count = FriendRequest.objects.filter(receiver=user, status="pending").count()
    context["pending_count"] = pending_count
    return render(request, "accounts/profile.html", context)


