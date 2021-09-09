from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, ChatRoom


class ProfileUpdateForm(forms.ModelForm):
    """
    form for updating the profile
    """

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'profile__input-text'
        self.fields['last_name'].widget.attrs['class'] = 'profile__input-text'
        self.fields['settings_message'].widget.attrs['class'] = 'profile__combobox'

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'image', 'settings_message')


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form__input'
        self.fields['password'].widget.attrs['class'] = 'form__input'


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form__input'
        self.fields['image'].widget.attrs['class'] = 'form__file'
        self.fields['first_name'].widget.attrs['class'] = 'form__input'
        self.fields['last_name'].widget.attrs['class'] = 'form__input'
        self.fields['password1'].widget.attrs['class'] = 'form__input'
        self.fields['password2'].widget.attrs['class'] = 'form__input'

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'image', 'first_name', 'last_name')


class SignUpForm1(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name')


class ChatRoomUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'chat-room__update-input'
        self.fields['image'].widget.attrs['class'] = 'chat-room__update-file'

    class Meta:
        model = ChatRoom
        fields = ('image', 'title')


class CreateChatRoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        friends_queryset = kwargs.pop('brand_queryset', None)
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'create-chat-room__file'
        self.fields['title'].widget.attrs['class'] = 'create-chat-room__input'
        self.fields['title'].widget.attrs['placeholder'] = 'Введите название бесед'

    class Meta:
        model = ChatRoom
        fields = ('title', 'image')


class AddUserChatRoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        friend_queryset = kwargs.pop('friend_queryset', None)
        super().__init__(*args, **kwargs)
        self.fields['users'].queryset = friend_queryset

    users = forms.ModelMultipleChoiceField(queryset=User.objects.none(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = ChatRoom
        fields = ('users',)
