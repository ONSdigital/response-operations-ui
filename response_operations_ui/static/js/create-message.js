 window.onload=function() {
   document.getElementById("employeeLink").onclick=function() {
     document.getElementById("myForm").submit();
     return false; // cancel the actual link
   }
 }