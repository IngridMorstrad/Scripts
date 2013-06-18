// A script by Ashwin Menon
// Automates voting on nam@et@h@ebu@m@p.com - URL obfuscated with '@'

// localStorage["name_list"] = JSON.stringify(); // To be executed initially - used if re-running the program

function defaultDict(map, normal) {
    return function(key) {
	if (key in map)
	    return map[key];
	//if (typeof default == "function")
	//return defaut(key);
	return normal;
    };
}
//Credit: http://stackoverflow.com/questions/13059837/javascript-array-with-default-values-equivalent-of-pythons-defaultdict

// var name_list = JSON.parse(localStorage["name_list"]); // Uncomment if re-running
var name_list = {};
var get_name_count = defaultDict(name_list, 0);

var ctr = 0;

// Adjust the following parameters as required
var votes_required = 10;
var gap_required = 200; // in milliseconds

function click_first_name() {
    var first_name = $($('a')[6]).text();
    var second_name = $($('a')[7]).text();
    name_list[first_name] = get_name_count(first_name) + 1;
    name_list[second_name] = get_name_count(second_name);
    $($('a')[6]).click();
    ctr++;
    if (ctr <= votes_required)
	window.setTimeout(click_first_name, gap_required);
    else {
	name_list
	    localStorage["name_list"] = JSON.stringify(name_list);
    }
}

click_first_name();

/*
   To try and populate "Current Rankings" - doesn't work yet.

   localStorage["bar"] = JSON.stringify(rr);

   function partC(name) {
   $('input[type=text]').val(name);
   $('input[type=submit]').click();  
   }

   window.location = "/add-name/";
   var qrrr = JSON.parse(localStorage["bar"]);
   for (name in qrrr) {
   window.setTimeout(partC(name),2000);
   window.location = "/add-name/";  
   }*/
