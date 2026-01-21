//add values of selected to check boxes and display totals
//ready for step 3B
         function calcTotal(){
            var def = 0;
            var cgh = ""
            var items = document.getElementsByTagName("input");
            //js variable items for all HTML elements w the input tag
            var ab="";
            var myTeam="";
            var hMod=0;
            var cgMod=0;

            for (var j = 0 ; j < 12; j++){
               if (items[j].checked){
                  var humanPlayer=j
                  myTeam=items[j].value.split("^");
                  def += Number(myTeam[0]);
                  var h=Number(myTeam[1].charAt(2));
                  console.log("Starting h is "+h)
                  cgMod+=Number(myTeam[1].charAt(1));
                  cgMod+=Number(myTeam[1].charAt(0));
                  console.log("My team cg mod is "+cgMod)
               }
            }
            console.log("Playing as " + humanPlayer)
            //split cgh based on team ID
            for (var i = 12; i < 24; i++){
               if (items[i].checked){//if the item is checked
                  var teamArray=items[i].value.split("^");
                  if (ab==""){
                     ab=teamArray[0];
                     ab=ab.split(",")
                     ab=ab[humanPlayer]
                     console.log("Final AB = " + ab)
                     cgh=teamArray[3];
                     cgh=cgh.split(",")
                     if (cgh.length!=12){
                        console.log("Error in length of cgh array. Length is "+cgh.length)
                     }
                     cgh=cgh[humanPlayer]
                     var c=parseInt(cgh.charAt(0),16)
                     var g=parseInt(cgh.charAt(1),16)
                     h+=parseInt(cgh.charAt(2),16);
                     console.log("After last defeated team; c, g, and h are " + c + "|"+g+"|"+h)
                  }else{
                     hMod=Number(teamArray[2].charAt(2));
                     h+=hMod;
                     if (hMod!=0){
                        console.log("hMod for " + i+ "= " + hMod+"")
                        console.log("New H = "+h)
                     }
                     cgMod+=Number(teamArray[2].charAt(1));
                     cgMod+=Number(teamArray[2].charAt(0));
                  }
                  def += Number(teamArray[1]);
                  console.log("After team " + i + " - def = " + def)
               }
            }
            console.log("Final raw value of H is "+h)
            if (h>=16){
               h=h%16;
               c+=1;
               console.log("Value of c increased to " + c)
            }
            console.log("h raw converts to " + h)
            console.log("cgMod="+cgMod);
            c+=cgMod
            console.log("Final c sum = " + c)
            g+=Math.floor(c/16)
            c=c%16
            console.log("Final C = " + c.toString(16))
            console.log("Final G = " + g.toString(16))
            h=h.toString(16).toUpperCase()
            console.log("The DEF = "+def.toString(16))
            console.log("Final H = "+h)
            c=c.toString(16).toUpperCase()
            g=g.toString(16).toUpperCase()
            //document.getElementById("total").innerHTML = "Password is " + ab + c + String(def.toString(16)).padStart(3,'0') + g + h+"\nGoal is "+goal+"||def="+ken;
               //inner HTML fills in the space between the opening and closing <p> tags with the total
            document.getElementById("total").innerHTML="Password is " + ab + c + String(def.toString(16).toUpperCase()).padStart(3,'0') + g + h;
         }
         document.getElementById("total").innerHTML = "Click below to calculate password"
         //backwards compatibility for event listener submit button
         var calcButton = document.getElementById("calcButton"); //sButton HTML element is assign JS value of submitButton
         if (calcButton.addEventListener){ //now you can add event listener
            calcButton.addEventListener("click", calcTotal, false); //event is click, action is calctotal, false for bwc
         }
         else if (calcButton.attachEvent){
            calcButton.attachEvent("onclick", calcTotal);
         }