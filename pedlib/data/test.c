/*
  =====[ AKOSTAR WiFi Clock project ]============================

   File Name:           lcd_imain.c

   Description:  Main file

   Revisions:

      REV   DATE            BY              DESCRIPTION
      ----  -----------     ----------      ------------------------------
      0.00  mar.27.2018     Peter Glen      Initial version.
      0.00  apr.15.2018     Peter Glen      Power management page

            21/08/19 11:47:24
   ======================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "driver/rtc_io.h"
#include "driver/i2c.h"
#include "soc/gpio_struct.h"
#include "esp_log.h"
#include "esp_console.h"
#include "esp_vfs_dev.h"
#include "driver/uart.h"
#include "linenoise/linenoise.h"
#include "argtable3/argtable3.h"
#include "esp_vfs_fat.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

#include "esp_wifi.h"
#include "esp_wpa2.h"
#include "esp_event_loop.h"
#include "esp_attr.h"
#include "esp32/ulp.h"
#include "esp_sleep.h"
#include "esp_smartconfig.h"
#include "esp_int_wdt.h"
#include "esp_task_wdt.h"
#include "esp_bt.h"
#include "driver/gpio.h"
#include "driver/adc.h"
#include "esp_adc_cal.h"

//#include "esp_clk.h"

#include "ulp_main.h"

// SNTP specific includes
#include "lwip/err.h"
#include "lwip/apps/sntp.h"
#include "lwip/sockets.h"
#include "esp_pm.h"

//#include "rom/ets_sys.h"
//#include "rom/crc.h"

#include "../../../common/v000/cutils.h"
#include "../../../common/v000/sutils.h"

#include "../../common/v001/utils.h"
#include "../../common/v001/wifi.h"
#include "../../common/v001/wlog.h"
#include "../../common/v001/cpu_load.h"

// Servers specific
#include "../../common/v001/httpd.h"
#include "../../common/v001/captdns.h"
#include "../../common/v001/wcrdate.h"
#include "../../common/v001/wcmesht.h"
#include "../../common/v001/gettime.h"
#include "../../common/v001/dst_algo.h"

#include "lcd_i2c.h"
#include "lcd7_i2c.h"
#include "lcd_imain.h"

extern const uint8_t ulp_main_bin_start[] asm("_binary_ulp_main_bin_start");
extern const uint8_t ulp_main_bin_end[]   asm("_binary_ulp_main_bin_end");

static void init_ulp_program();
static void update_pulse_count();

//! User settable parameters

#define   HUMIDITY_COUNT   10               //!< How many secs between humidity meas.
#define   TEMP_COUNT       8                //!< How many secs between temp meas.
#define   BATT_COUNT       12               //!< How many secs between batt meas.

#define   BAD_LIM         2 * 60            //!<  Bad clock retry limit
#define   BAD_HOUR_LIM    1 * 60 * 60       //!<  Bad clock hourly limit
#define   BAD_TRY_CYCLES  6                 //!<  Bad clock retry cycle limit

//! Bad counts subsystem

#define   BAD_RETRY_TRESH   2 * 60          //!<  Bad clock retry limit (2 minutes)
#define   BAD_RETRY_MAX     6               //!<  Bad clock retry cycle limit
#define   BAD_SHOW_DOTS     3               //!<  Dots ON after this many bad tries

// These variables contain data preserved across deep sleep

static RTC_DATA_ATTR uint32_t rtc_boot_cnt;
static RTC_DATA_ATTR struct timeval sleep_enter_time;

// This variable contains wake status

static  int     gl_waker = 0;

//! Error handling related

static  int     gl_bad_tresh    = BAD_RETRY_TRESH;

static  int     gl_bad_cumm     = 0;           //!< Cummulative bad count
static  int     gl_bad_count    = 0;           //!< Cyclical bad count
static  int     gl_bad_try      = 0;           //!< Number of cycles
static  int     gl_bad_showdots = 0;           //!< Show double dots
static  int     gl_blink_wifi   = 0;
static  int     gl_good_wifi    = 0;
static  int     gl_wifi_cnt     = 0;

//! Eval tick shoulder

static  int     gl_evaltick       = 1;
static  int     gl_gotmintran     = 0;
static  int     gl_minute         = 0;
static  int     gl_got_client     = 0;

//! Error related variables
static  int     gl_error = 0, gl_errcnt = 0, gl_errflag = 0;

int     gl_but_down = 0;

//{
char *build_and_ver = "WiFiClock LCD Ver. 1.0 Built: Tue, 9 Apr";
//}

/*! \name Sensors and Power
 */
///@{
int     gl_temp_cal = 0;                //!< Calibration temp %
int     gl_humi_cal = 0;                //!< Calibration humidity &
int     gl_cont_cal = 0;                //!< Calibration humidity &
int     gl_minmod = 0;                  //!< Minute mode
int     gl_humioff = 0;                 //!< Humidity sensor
int     gl_tempoff = 0;                 //!< Temperature sensor

int     gl_modem_on = 0;                 //!< Modem [RF] on
int     gl_bad_fmode = 0;               //!< Are we in failure mode?
int     gl_rf_pow = RFPOW_HIGH;         //!< RF power level
int     gl_wifiatt = WIFI_ATTEM1;       //!< Number of wifi attempts

///@}

/*! \name Sleep related
 */

int     gl_modemsleep     = 0;
uint    gl_modemcnt       = 0;

/*! \name Countdown countup timer related
 */
 ///@{
int     gl_countup = false;
int     gl_timer_inits = 30;            //!< Initial timer value in secs
int     gl_timer_initm = 0;             //!< Initial timer value in mins
int     gl_timer_on = false;
int     gl_timer_go = false;
int     gl_timer_mins = 0;
int     gl_timer_secs = 0;
 ///@}

/*! \name CountUp timer related
 */
///@{
int     gl_uptimer_on = false;
int     gl_uptimer_go = false;
int     gl_uptimer_secs = 0;
int     gl_uptimer_mins = 0;
///@}

int     gl_kiosk = false;
int     gl_kiosk_num = 0;

int     gl_timer_blink = 0;
int     gl_wasboot = 1;                 //!< Flag for identifing fresh boot

float    gl_temp_calib = 0;

//! 12 hour default, DST default, count up limit

int     gl_celsius = false;             //!< Show in celsius else fahrenheit
int     gl_var_24  = false;             //!< Flag for 12/24 [24 if true]

//int   gl_countlim = 8 * 60 * 60;
int     gl_countlim = 24 * 60 * 60;

uint64_t gl_lastserve = 0;

// -----------------------------------------------------------------------
// Private

static const char *TAG = "i2c-clock";

static SemaphoreHandle_t ttSemaphore  = NULL;
static int  ttask_in = false;
static int  gl_reboot = 0;          //!<  Reboot requested

// -----------------------------------------------------------------------
// Persistent

int     gl_last_try = 0;
char    gl_tz[12]        = "EST+5DST";  //!< TZ val
char    gl_cus[12]       = "EST+5";     //!< TZ value
char    gl_colnm[12]     = "WW";        //!< Color name
char    gl_sernm[24]     = "";          //!< Custom server name
char    gl_prefnm[24]    = "";          //!< Preferred
char    gl_dst[12]       = "";          //!< DST on off aut

char    gl_cust_ip[24]   = "";          //!< Custom IP
char    gl_cust_ip2[24]  = "";          //!< Custom IP2
char    gl_cust_ip3[24]  = "";          //!< Custom IP3
char    gl_sel_ip[24]    = "";          //!< Selected IP

char    gl_other_nm[36]  = "";
char    gl_other_pa[36] = "";
char    gl_other_nm2[36] = "";
char    gl_other_pa2[36] = "";
int     gl_other = 0;

int     gl_bright_per    = 20;
int     gl_custz         = 0;           //!< Custom time zone OK
int     gl_cuscol        = 0;           //!< Custom color OK
int     gl_custser       = 0;           //!< Custom time server OK
int     gl_manual        = 0;           //!< If manual override
int     gl_dst_flag      = 0;           //!< DST flag
int     gl_leadz         = 0;           //!< Leading zero showing

int     gl_rr = 255;
int     gl_gg = 255;
int     gl_bb = 255;
int     gl_crr = 255;
int     gl_cgg = 255;
int     gl_cbb = 255;
int     gl_nodots = 0;
int     gl_attention = false;

int     gl_effect = 0;                  //!< Effect in operation
int     gl_restart_ntp = 0;             //!< Keep going with NTP

// Shared

int     gl_countup_on = false;
int     gl_wiflag = 1;

// -----------------------------------------------------------------------
// Back off with the connectivity, dependent on state
//

static void sleep_wifi()

{
    printf("Sleeping modem now.\n");
    if(is_wifi_connected())
        {
        printf("Disconnecting WiFi ...\n");
        wifi_disconnect();
        vTaskDelay(200 / portTICK_PERIOD_MS);
        }
    esp_wifi_stop();
    vTaskDelay(200 / portTICK_PERIOD_MS);
    esp_wifi_deinit();
    gl_modemsleep = true;
    printf("WiFi sleeping.\n");
}

// -----------------------------------------------------------------------
//

static void    wake_wifi()

{
    wifi_preinit("lcd");

    // Read WIFI parms
    read_wifi_config();

    wcwifi_sta_init(stname, stpass);
    wcwifi_ap_init(apname, appass);

    // Wifi recovery  (superseeded by manufacturer's reset)
    //wcwifi_sta_init("", "");
    //wcwifi_ap_init("", "");

    ESP_LOGI(TAG, "Waiting for wifi subsys to come online ...");
    xEventGroupWaitBits(wifi_event_group, AP_START_BIT,
                                    false, true, portMAX_DELAY);

    ESP_LOGI(TAG, "Got wifi subsys.");
    // ---------------------------------------------------------------
    // WIFI NET UP, do netconfig

    // Start DNS Server
    captdnsInit();
    //ESP_LOGI(TAG, "Started DNS server.");

    // Start HTTP Server
    init_httpd(0);
    //ESP_LOGI(TAG, "Started HTTP server.");

    // Start RDATE Server
    //init_rdated(0);
    //ESP_LOGI(TAG, "Started RDATE server.");

    // Start MESHT Server
    struct ip4_addr iadd; iadd.addr = IPADDR_ANY;
    init_meshtd(iadd);
    //ESP_LOGI(TAG, "Started Mesh Time server.");
}

#if 0

// Tell the log where the time was from

//////////////////////////////////////////////////////////////////////////
//

static char    *time_server_str()

{
    char *ppp = "Defaults";

    if(gl_custser == 1)
        ppp = gl_sernm;
    if(gl_custser == 2)
        ppp = gl_cust_ip;

    return ppp;
}

#endif

//////////////////////////////////////////////////////////////////////////
// Get time from server as a task

static  void    timeTask(void *pvParameters)

{
    gl_blink_wifi = true;

    gl_wifi_cnt = 0;

    DO_FOREVER
        {
        gl_restart_ntp = false;

        vTaskDelay(10 / portTICK_RATE_MS);
        srand(esp_timer_get_time());

        ESP_LOGI(TAG, "timeTask() started at %d rand %d",
                        (int)(esp_timer_get_time() / 1000), rand());
        int cnt = 10;
        DO_FOREVER
            {
            gl_last_try = (int)(esp_timer_get_time() / 1000);

            if(!is_wifi_connected())
                {
                // Will wait ...
                wifi_connect();
                }
            //printf("Getting internet time.\n");
            if(is_wifi_connected())
                {
                ESP_LOGI(TAG, "Waiting for connection to time server ...");

                gl_good_wifi = true;

                // Fresh cycle
                gl_countup = 0; gl_wasboot = false;

                time_t now2 = internet_gettime();

                struct  tm timeinfo2 = { 0 };
                localtime_r(&now2, &timeinfo2);

                // If we got good time, break out
                if(timeinfo2.tm_year > (2016 - 1900))
                    {
                    //char *ppp = time_server_str();
                    //wlog_event(CLOCK_GOT_TIME, secs_from_start() % 1000, ppp);

                    ESP_LOGI(TAG,
                       "Got time from time server: %d/%s/%d  %02d:%02d:%02d",
                            timeinfo2.tm_mday, convmonth(timeinfo2.tm_mon + 1),
                             timeinfo2.tm_year + 1900,
                              timeinfo2.tm_hour, timeinfo2.tm_min,
                                timeinfo2.tm_sec);

                    // Got valid time, reset status and bad counts
                    gl_manual = false;
                    //gl_bad_try = gl_bad_count = 0; // Reset failure counts
                    //gl_badlim_cnt = BAD_LIM;

                    // Success .. reset failure counts and flags
                    gl_bad_fmode =  gl_bad_cumm = 0;
                    gl_bad_try = gl_bad_count = 0;
                    gl_bad_cumm = gl_bad_showdots = 0;
                    gl_bad_tresh  = BAD_RETRY_TRESH;

                    break;
                    }
                ESP_LOGE(TAG, "Could not obtain internet time.\n");
                gl_bad_fmode = true;
                show_error(false, 88, false);  // No internet time
                //char bt[12]; snprintf(bt, sizeof(bt), "%d", gl_bad_try);
                //wlog_event(CLOCK_ERR_TIME, secs_from_start() % 1000, bt);
                }
            else
                {
                // This could be reported right away
                gl_bad_fmode = true;
                ESP_LOGE(TAG, "Could not connect to wifi.\n");
                char bt[12]; snprintf(bt, sizeof(bt), "%d", gl_bad_try);
                //wlog_event(CLOCK_WIFI_ERR, secs_from_start() % 1000, bt);

                //if(gl_bad_try < 3)
                //    show_error(false, 77, false); // No Wifi

                gl_good_wifi = false;
                }

             if(gl_other)
                {
                wifi_disconnect();
                gl_lastserve = 0;
                //printf("Calling peer_gettime()");

                int dist = 0;
                time_t now3 = peer_gettime(&dist);

                struct  tm timeinfo3 = { 0 };
                localtime_r(&now3, &timeinfo3);

                // If we got good time, break out
                if(timeinfo3.tm_year > (2016 - 1900))
                    {
                    ESP_LOGI(TAG,
                       "Got time from peer: %d/%s/%d  %02d:%02d:%02d",
                            timeinfo3.tm_mday, convmonth(timeinfo3.tm_mon + 1),
                              timeinfo3.tm_year + 1900,
                               timeinfo3.tm_hour, timeinfo3.tm_min,
                                 timeinfo3.tm_sec);
                    break;
                    }
                }

            // Just a little delay, so the rest can settle
            vTaskDelay(300 / portTICK_PERIOD_MS);

            // Valid time?
            time_t now; struct  tm timeinfo = { 0 };
            time(&now); localtime_r(&now, &timeinfo);
            if(timeinfo.tm_year > (2016 - 1900) ||
                                gl_countup >= gl_countlim || gl_wasboot)
                {
                ESP_LOGI(TAG,
                    "timeTask() getting clock. cycle: %d last_try time %d",
                                                cnt, gl_last_try);

                // Save first time we aquire valid time ...
                //  ... for manufacturer's information

                time_t now3; struct  tm timeinfo3 = { 0 };
                now3 = add_firstcount(now);
                localtime_r(&now3, &timeinfo3);
                ESP_LOGI(TAG,
                    "Got first time value: %d/%s/%d  %02d:%02d:%02d",
                         timeinfo3.tm_mday, convmonth(timeinfo3.tm_mon + 1),
                            timeinfo3.tm_year + 1900,
                              timeinfo3.tm_hour, timeinfo3.tm_min,
                                timeinfo3.tm_sec);
                break;
                }
            // Counter?
            BREAK_IF(cnt <= 0)
            // Restart?
            BREAK_IF(gl_restart_ntp == false)

            //cnt--;
            }

        // Let the WiFi hang on for a while ... server may respond
        vTaskDelay(300 / portTICK_PERIOD_MS);
        // After getting time, disconnect
        wifi_disconnect();
        gl_lastserve = 0;

        TAKE_SEMA( ttSemaphore, TAG, 100);
        ttask_in = false;
        GIVE_SEMA( ttSemaphore );

        ESP_LOGI(TAG, "timeTask() ended.");

        BREAK_IF(gl_restart_ntp == false)
        }

    if(!is_valid_time(NULL))
        {
        //char *ppp = time_server_str();
        //wlog_event(CLOCK_ERR_TIME, secs_from_start() % 1000, ppp);
        }

    gl_evaltick = true;
    gl_blink_wifi = false;

    vTaskDelete(NULL);
}

# EOF