
template = ("""
<div class="wrapper">
    <div class="header">
    <div class="shop-title">
    <img src="https://cdn.shopify.com/s/files/1/0463/6098/5764/files/1080_B_C_short_845ea474-14bb-4794-bfd7-c75c5beb7d8f.png?v=1600620183"; style="width: 240px; height: 120px;">
    </div>
    <div class="order-title">
    <p class="text-align-right-large">
    Order #{orderID}
    </p>
    <p class="text-align-right">
    Date: {delivery_date}
    </p>
    </div>
    </div>
    <div class="customer-addresses">
    <div class="shipping-address">
    <p class="subtitle-bold to-uppercase">
    Delivery to
    </p>
    <p class="address-detail">
    {shipping_address}
    </p>
    </div>
    <div class="billing-address">
    <p class="subtitle-bold to-uppercase">
    Bill to
    </p>
    <p class="address-detail">
    {billing_address}
    </p>
    </div>
    </div>

    <hr>
    <div class="order-container">
    <div class="order-container-header">
    <div class="order-container-header-left-content">
    <p class="subtitle-bold to-uppercase">
    Items
    </p>
    </div>
    <div class="order-container-header-right-content">
    <p class="subtitle-bold to-uppercase">
    Quantity
    </p>
    </div>
    </div>
   
    {lineitems}
    
    </div>
    <hr>
    <div class="notes">
    <p class="notes-details to-uppercase">
    Notes
    </p>
    <p class="notes-details">
    {ordernotes}
    </p>
    </div>

    <!-- 
    {{% if delivery_method.instructions != blank %}}
    <div class="notes">
    <p class="subtitle-bold to-uppercase">
    Delivery instructions
    </p>
    <p class="notes-details">
    {{ delivery_method.instructions }}
    </p>
    </div>
    {{% endif %}} -->

    <div class="footer">
    <p>
    <strong>
    {shop_name}
    </strong>
    <br>
    {shop_email}
    <br>
    {shop_domain}
    </p>
    </div>

    <div class="package-delivery-info">
    <p>    
    Route: {routename}
    <br>
    Stop: {stopnumber}
    <br>
    Bike: {bikename}
    </p>
    </div>

   </div>
   <style type="text/css">
    body {{
    font-size: 15px;
    }}
   
    * {{
    box-sizing: border-box;
    }}
   
    .wrapper {{
    width: 831px;
    margin: auto;
    padding: 4em;
    font-family: "Noto Sans", sans-serif;
    font-weight: 250;
    }}
   
    .header {{
    width: 100%;
    display: -webkit-box;
    display: -webkit-flex;
    display: flex;
    flex-direction: row;
    align-items: top;
    }}
   
    .header p {{
    margin: 0;
    }}
   
    .shop-title {{
    -webkit-box-flex: 6;
    -webkit-flex: 6;
    flex: 6;
    font-size: 1.9em;
    }}
   
    .order-title {{
    -webkit-box-flex: 4;
    -webkit-flex: 4;
    flex: 4;
    }}
   
    .customer-addresses {{
    width: 100%;
    display: inline-block;
    margin: 2em 0;
    }}
   
    .address-detail {{
    margin: 0.7em 0 0;
    line-height: 1.5;
    }}
   
    .subtitle-bold {{
    font-weight: bold;
    margin: 0;
    font-size: 0.85em;
    }}
   
    .to-uppercase {{
    text-transform: uppercase;
    }}
   
    .text-align-right {{
    text-align: right;
    }}
   
    .text-align-right-large {{
    text-align: right;
    font-size: 24px;
    }}

    .shipping-address {{
    float: left;
    min-width: 18em;
    max-width: 50%;
    }}
   
    .billing-address {{
    padding-left: 20em;
    min-width: 18em;
    }}
   
    .order-container {{
    padding: 0 0.7em;
    }}
   
    .order-container-header {{
    display: inline-block;
    width: 100%;
    margin-top: 1.4em;
    }}
   
    .order-container-header-left-content {{
    float: left;
    }}
   
    .order-container-header-right-content {{
    float: right;
    }}
   
    .flex-line-item {{
    display: -webkit-box;
    display: -webkit-flex;
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 1.4em 0;
    page-break-inside: avoid;
    font-size: 20px;
    }}
   
    .flex-line-item-img {{
    margin-right: 1.4em;
    min-width: 58px;
    }}
   
    .flex-line-item-description {{
    -webkit-box-flex: 7;
    -webkit-flex: 7;
    flex: 7;
    }}
   
    .line-item-description-line {{
    display: block;
    }}
   
    .flex-line-item-description p {{
    margin: 0;
    line-height: 1.5;
    }}
   
    .flex-line-item-quantity {{
    -webkit-box-flex: 3;
    -webkit-flex: 3;
    flex: 3;
    }}
   
    .subdued-separator {{
    height: 0.07em;
    border: none;
    color: lightgray;
    background-color: lightgray;
    margin: 0;
    }}
   
    .missing-line-items-text {{
    margin: 1.4em 0;
    padding: 0 0.7em;
    }}
   
    .notes {{
    margin-top: 2em;
    }}
   
    .notes p {{
    margin-bottom: 0;
    }}
   
    .notes .notes-details {{
    margin-top: 0.7em;
    font-size: 24px;
    font-weight: bold;
    }}
   
    .footer {{
    margin-top: 2em;
    text-align: center;
    line-height: 1.5;
    }}
   
    .footer p {{
    margin: 0;
    margin-bottom: 1.4em;
    }}
   
    hr {{
    height: 0.14em;
    border: none;
    color: black;
    background-color: black;
    margin: 0;
    }}
   
    .aspect-ratio {{
    position: relative;
    display: block;
    background: #fafbfc;
    padding: 0;
    }}
   
    .aspect-ratio::before {{
    z-index: 1;
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    border: 1px solid rgba(195,207,216,0.3);
    }}
   
    .aspect-ratio--square {{
    width: 100%;
    padding-bottom: 100%;
    }}
   
    .aspect-ratio__content {{
    position: absolute;
    max-width: 100%;
    max-height: 100%;
    display: block;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    margin: auto;
    }}

    .package-delivery-info{{
    margin-top: 1cm;
    font-size: 16;
    font-weight: bold;
    }}

   </style>
""")
   