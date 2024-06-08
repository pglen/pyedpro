#include <gtk/gtk.h>
#include <gtk/gtkx.h>
#include <stdio.h>
#include <stdlib.h>

int main(int ac, char **av)
{
    GtkWidget *window;
    GtkWidget *socket;

    gtk_init(&ac, &av);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    socket = gtk_socket_new();
    gtk_window_set_title(window, "some socket");
    gtk_window_set_position(window, GTK_WIN_POS_CENTER);

    gtk_container_add(window, socket);// added socket into window
    g_signal_connect(GTK_WIDGET(window), "destroy", gtk_main_quit, NULL);

    printf("socket ID: %d\n", gtk_socket_get_id(socket));

    char buffer[1024];
    sprintf(buffer, "python3 ./plug.py %d &", gtk_socket_get_id(socket));
    system(buffer);

    gtk_widget_show_all(window);
    gtk_main();

    return 0;
}
