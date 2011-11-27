var sizes = [13, 16, 19];
var classes = ["scale1", "scale2", "scale3"];

function resizeFonts(index)
{
	var body = document.getElementsByTagName('body');
	for (i = 0; i < body.length; i++)
	{
		body[i].style.fontSize = sizes[index] + 'px';
	}
	
	for (i = 0; i < classes.length; i++)
	{
		var objs = document.getElementsByClassName(classes[i]);
		if (i == index)
		{
			for (j = 0; j < objs.length; j++)
			{
				objs[j].style.textDecoration = "underline";
			}
		}
		else
		{
			for (j = 0; j < objs.length; j++)
			{
				objs[j].style.textDecoration = "none";
			}
		}
	}
}