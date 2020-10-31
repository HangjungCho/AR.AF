var happy_timer			= new Array();
var happy_timer_layer	= 'timer_print_layer_';
var happy_timer_started	= false;
var happy_timer_len		= 0;

function happy_timer_value( num, restTime )
{
	if ( document.getElementsByName(happy_timer_layer+num) != undefined )
	{
		happy_timer[num]		= parseInt(restTime);

		if ( happy_timer_started === false )
		{
			happy_timer_call();
			happy_timer_started		= true;
		}
	}
}

function happy_timer_call()
{
	var old_onload			= window.onload;

	if ( typeof window.onload != 'function' )
	{
		window.onload			= function()
		{
			happy_timer_len		= happy_timer.length;
			happy_timer_start();
		}
	}
	else
	{
		window.onload			= function()
		{
			old_onload();

			happy_timer_len		= happy_timer.length;
			happy_timer_start();
		}
	}
}


function happy_timer_start()
{
	var now_timer_obj		= '';
	var now_num				= '';
	var now_restTime		= 0;
	var i					= 0;

	for ( now_num in happy_timer )
	{
		now_timer_obj			= document.getElementsByName(happy_timer_layer+now_num);
		if ( now_timer_obj != undefined )
		{
			now_restTime			= happy_timer_restTime_change(happy_timer[now_num]);
			for ( i=0 ; i<now_timer_obj.length ; i++ )
			{
				if ( now_timer_obj[i].value != undefined )
				{
					now_timer_obj[i].value		= now_restTime;
				}
			}
			happy_timer[now_num]--;
		}
	}

	setTimeout('happy_timer_start()',1000);
}


function happy_timer_restTime_change(restTime)
{
	var happy_timer_result	= '';

	if ( restTime <= 0 )
	{
		happy_timer_result		= '판매가 종료되었습니다';
	}
	else
	{
		var happy_timer_day		= Math.floor(restTime/86400);
		var happy_timer_hour	= Math.floor((restTime%86400)/3600);
		var happy_timer_min		= Math.floor((restTime%3600)/60);
		var happy_timer_sec		= Math.floor(restTime%60);

		if ( happy_timer_day > 0 )
		{
			happy_timer_result		+= happy_timer_day + '일 ';
		}

		if ( happy_timer_hour > 0 )
		{
			happy_timer_result		+= happy_timer_hour + '시간 ';
		}

		if ( happy_timer_min > 0 )
		{
			happy_timer_result		+= happy_timer_min + '분 ';
		}

		if ( happy_timer_sec > 0 )
		{
			happy_timer_result		+= happy_timer_sec + '초';
		}
	}


	return happy_timer_result;
}