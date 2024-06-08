# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


urlpatterns = [

    # USER
    path("", views.index, name="index"),
    path('user_login/', LoginView.as_view(template_name='user/user_login.html'), name='user_login'),
    path("signup/", views.signup, name="signup"),
    path("user_homepage/", views.user_homepage, name="user_homepage"),
    path("logout/", views.Logout, name="logout"),
    path("all_notices/", views.all_notices, name="all_notices"),
    path("notice_detail/<int:myid>/", views.notice_detail, name="notice_detail"),
    path("notice_apply/<int:myid>/", views.notice_apply, name="notice_apply"),
    path("callback", views.payment_response, name="payment_status"),
    path("user_applications/", views.user_applications, name="user_applications"),
    path('user/payments/', views.user_payment_list, name='user_payment_list'),
    path("notice_submit/<int:myid>/", views.notice_submit, name="notice_submit"),
    path("user_submissions/", views.user_submissions, name="user_submissions"),
    path('chat/', views.chat, name='chat'),

# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________


    # ADMIN
    
    path("admin_home/", views.admin_home_view, name="admin_home"),
    path("add_notice/", views.add_notice, name="add_notice"),
    path("notice_list/", views.notice_list, name="notice_list"),
    path("edit_notice/<int:myid>/", views.edit_notice, name="edit_notice"),
    path("all_applicants/", views.all_applicants, name="all_applicants"),
    path("admin_login/", views.admin_login, name="admin_login"),
    path("view_applicants/", views.view_applicants, name="view_applicants"),
    path("delete_applicant/<int:myid>/", views.delete_applicant, name="delete_applicant"),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('payment_list/', views.payment_list, name='payment_list'),
    path('notice/<int:pk>/delete/', views.NoticeDeleteView.as_view(), name='notice_delete'),
    path('payments/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('add_application/', views.add_application, name='add_application'),
    path('edit_applicant/<int:applicant_id>/', views.edit_applicant, name='edit_applicant'),
    path("all_submissions/", views.all_submissions, name="all_submissions"),
    path('delete_order3/', views.delete_order3, name='delete_order3'),   
    path('messages/', views.admin_messages, name='admin_messages'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),

    path('form11/<int:myid>/', views.form11_view, name='form11_view'),






    # path('notice/<int:notice_id>/emails/', views.get_applicant_emails_by_notice, name='notice_emails'),

    path('notice/emails/', views.get_applicant_emails, name='applicant_emails'),
# __________________________________________________________________________________________________________________________________________________________________________________________________________________________________
 

    path('view_biddoc_images/<int:notice_id>/', views.view_biddoc_images, name='view_biddoc_images'),
    path('view_full_notice_images/<int:notice_id>/', views.view_full_notice_images, name='view_full_notice_images'),



    path('admin_view_biddoc_images/<int:notice_id>/', views.admin_view_biddoc_images, name='admin_view_biddoc_images'),
    path('admin_view_full_notice_images/<int:notice_id>/', views.admin_view_full_notice_images, name='admin_view_full_notice_images'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    